from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.core.cache import cache
from .product import Product

from store.utils import select_for_update, convert_string_to_decimal


class Order(models.Model):
    date_time = models.DateTimeField(auto_now_add=True)
    # user = models.ForeignKey(
    #     settings.AUTH_USER_MODEL
    # )

    @transaction.atomic
    def add_details(self, details):
        insufficient_stock_products = []
        for detail in details:
            product = select_for_update(Product, detail['product'].id)
            stock = product.stock
            cuantity = detail['cuantity']
            if product.check_stock(cuantity):
                product.set_stock(abs(stock - cuantity))
                OrderDetail.objects.create(
                    order_id=self.id, **detail
                )
            else:
                insufficient_stock_products.append(product)

        if insufficient_stock_products:
            self.throw_stock_error(
                insufficient_stock_products
            )

    @staticmethod
    def throw_stock_error(products_out_stock):
        products_name = [product.name for product in products_out_stock]
        string_products_name = ", ".join(products_name)
        entity = 'Product'
        if len(products_name) > 1:
            entity += 's'

        raise ValidationError(
            f"{entity} {string_products_name} do not have enough stock"
        )

    @transaction.atomic
    def update_details(self, details_to_update, current_details):
        insufficient_stock_products = []
        for detail in details_to_update:
            product = select_for_update(Product, detail['product'].id)
            stock = product.stock
            new_cuantity = detail['cuantity']
            current_detail = self.get_current_detail(
                current_details,
                product.id
            )
            current_cuantity = current_detail.cuantity
            deductions = self.get_deduction(new_cuantity, current_cuantity)

            if new_cuantity < current_cuantity:
                product.set_stock(stock + deductions)

            if new_cuantity > current_cuantity:
                product.set_stock(stock - deductions)

                if self.is_out_stock(deductions, stock):
                    insufficient_stock_products.append(product)

            current_detail.cuantity = new_cuantity
            current_detail.save()

        if insufficient_stock_products:
            self.throw_stock_error(
                insufficient_stock_products
            )

    def delete_details(self):
        details = self.details.all()
        for detail in details:
            detail.restore_stock()
            detail.delete()

    @staticmethod
    def is_out_stock(deductions, stock):
        if deductions > stock:
            return True

    def get_deduction(self, new, current):
        return abs(new - current)

    @staticmethod
    def get_current_detail(current_details, product_id):
        for detail in current_details:
            if detail.product.id == product_id:
                return detail

    @staticmethod
    def get_details_to_update_and_create(details, current_details):
        to_add = []
        to_update = []
        products_ids = [detail.product.id for detail in current_details]
        for detail in details:
            product_id = detail['product'].id
            if product_id in products_ids:
                to_update.append(detail)
            else:
                to_add.append(detail)

        return {"to_add": to_add, "to_update": to_update}

    @property
    def get_total(self):
        return sum(detail.get_cost() for detail in self.details.all())

    @property
    def get_total_usd(self):
        total = self.get_total
        dolar_blue = cache.get("dolar_blue")
        if dolar_blue is None:
            return None
        total_usd = total / convert_string_to_decimal(dolar_blue)
        return float(format(total_usd, ".2f"))


class OrderDetail(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="details"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="orders_detail"
    )
    cuantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(1)]
    )

    @transaction.atomic
    def restore_stock(self):
        product = select_for_update(Product, self.product.id)
        stock = product.stock
        product.set_stock(stock + self.cuantity)

    def get_cost(self):
        return self.product.price * self.cuantity
