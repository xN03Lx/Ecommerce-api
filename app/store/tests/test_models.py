from unittest.mock import patch
from django.test import TestCase
from django.core.exceptions import ValidationError
from store.models import Product, Order, OrderDetail


def sample_order():
    return Order.objects.create()


def sample_product(**params):
    defaults = {
        'name': 'test product',
        'stock': 10,
        'price': 50.00
    }
    defaults.update(params)
    return Product.objects.create(**defaults)


class ProductModelTest(TestCase):

    def test_set_stock(self):
        product = Product.objects.create(
            name="testproduct",
            stock=5,
            price=10.00
        )
        new_stock = 20
        product.set_stock(new_stock)
        self.assertEqual(product.stock, 20)

    def test_check_stock_invalid_cuantity(self):
        product = Product.objects.create(
            name="testproduct",
            stock=5,
            price=10.00
        )
        cuantity = 10
        self.assertFalse(product.check_stock(cuantity))

    def test_check_stock_valid_cuantity(self):
        product = Product.objects.create(
            name="testproduct",
            stock=5,
            price=10
        )
        cuantity = 5
        self.assertTrue(product.check_stock(cuantity))


class OrderDetailModelTest(TestCase):

    def test_get_cost(self):
        price = 100.00
        product = sample_product(price=price)
        order = sample_order()
        order_detail = OrderDetail.objects.create(
            order=order,
            product=product,
            cuantity=3
        )
        expected_output = price * 3
        self.assertEqual(expected_output, order_detail.get_cost())

    def test_restore_stock(self):
        stock = 20
        product = sample_product(stock=stock)
        order = sample_order()
        cuantity = 10
        order_detail = OrderDetail.objects.create(
            order=order,
            product=product,
            cuantity=cuantity
        )
        total_stock = abs(stock - cuantity)
        product.set_stock(total_stock)
        order_detail.restore_stock()
        order_detail.product.refresh_from_db()
        self.assertEqual(stock, order_detail.product.stock)


class OrderModelTest(TestCase):

    def test_add_details_successful(self):
        product1 = sample_product(name="product 1", stock=10)
        product2 = sample_product(name="product 2", stock=10)
        payload = [
            {"product": product1, "cuantity": 3},
            {"product": product2, "cuantity": 5},
        ]
        order = Order.objects.create()
        order.add_details(payload)
        details = order.details.all()
        self.assertEqual(order.details.count(), len(payload))
        self.assertEqual(payload[0]['cuantity'], details[0].cuantity)
        self.assertEqual(product1, details[0].product)
        self.assertEqual(payload[1]['cuantity'], details[1].cuantity)
        self.assertEqual(product2, details[1].product)

    def test_add_details_invalid(self):
        product1 = sample_product(name="product 1", stock=10)
        product2 = sample_product(name="product 2", stock=2)
        payload = [
            {"product": product1, "cuantity": 10},
            {"product": product2, "cuantity": 5},
        ]
        order = Order.objects.create()
        try:
            order.add_details(payload)
        except ValidationError:
            self.assertRaises(ValidationError)

    def test_is_out_stock(self):
        deductions = 25
        stock = 20
        self.assertTrue(Order.is_out_stock(deductions, stock))

    def test_throw_stock_error_multiple_products(self):
        product1 = sample_product(name="product 1", stock=10)
        product2 = sample_product(name="product 2", stock=20)
        try:
            Order.throw_stock_error([product1, product2])
        except ValidationError as e:
            self.assertRaises(ValidationError)
            msg = 'Products product 1, product 2 do not have enough stock'
            self.assertEqual(e.message, msg)

    def test_throw_stock_error_single_product(self):
        product1 = sample_product(name="product 1", stock=10)
        try:
            Order.throw_stock_error([product1])
        except ValidationError as e:
            self.assertRaises(ValidationError)
            msg = 'Product product 1 do not have enough stock'
            self.assertEqual(e.message, msg)

    def test_get_current_detail(self):
        product1 = sample_product(name="product 1", stock=10)
        product2 = sample_product(name="product 2", stock=10)
        payload = [
            {"product": product1, "cuantity": 3},
            {"product": product2, "cuantity": 5},
        ]
        order = Order.objects.create()
        order.add_details(payload)
        current_details = order.details.all().select_related('product')
        detail1 = order.get_current_detail(current_details, product1.id)
        detail2 = order.get_current_detail(current_details, product2.id)

        self.assertEqual(current_details[0], detail1)
        self.assertEqual(current_details[1], detail2)

    def test_get_total(self):
        price1 = 20.00
        price2 = 30.00
        product1 = sample_product(name="product 1", price=price1)
        product2 = sample_product(name="product 2", price=price2)
        payload = [
            {"product": product1, "cuantity": 3},
            {"product": product2, "cuantity": 5},
        ]
        order = Order.objects.create()
        order.add_details(payload)
        expected_output = (price1 * 3) + (price2 * 5)
        self.assertEqual(order.get_total, expected_output)

    @patch('store.models.orders.cache.get')
    def test_get_total_usd(self, mock_get_dollar_blue):
        mock_get_dollar_blue.return_value = "217.00"
        price1 = 20.00
        price2 = 30.00
        product1 = sample_product(name="product 1", price=price1)
        product2 = sample_product(name="product 2", price=price2)
        payload = [
            {"product": product1, "cuantity": 3},
            {"product": product2, "cuantity": 5},
        ]
        order = Order.objects.create()
        order.add_details(payload)
        total = ((price1 * 3) + (price2 * 5))
        expected_output = float(format((total / 217.00), ".2f"))
        self.assertEqual(order.get_total_usd, expected_output)

    @patch('store.models.orders.cache.get')
    def test_get_total_usd_invalid(self, mock_get_dollar_blue):
        mock_get_dollar_blue.return_value = None
        price1 = 20.00
        price2 = 30.00
        product1 = sample_product(name="product 1", price=price1)
        product2 = sample_product(name="product 2", price=price2)
        payload = [
            {"product": product1, "cuantity": 3},
            {"product": product2, "cuantity": 5},
        ]
        order = Order.objects.create()
        order.add_details(payload)
        self.assertEqual(order.get_total_usd, None)

    def test_update_details_successful(self):
        product1 = sample_product(name="product 1", stock=10)
        product2 = sample_product(name="product 2", stock=15)
        product3 = sample_product(name="product 3", stock=5)
        order = Order.objects.create()
        payload = [
            {"product": product1, "cuantity": 3},
            {"product": product2, "cuantity": 5},
            {"product": product3, "cuantity": 1},
        ]
        order.add_details(payload)
        payload_to_update = [
            {"product": product1, "cuantity": 1},
            {"product": product2, "cuantity": 10},
            {"product": product3, "cuantity": 1},
        ]
        current_details = order.details.all()
        order.update_details(payload_to_update, current_details)
        product1.refresh_from_db()
        product2.refresh_from_db()
        product3.refresh_from_db()
        self.assertEqual(product1.stock, 9)
        self.assertEqual(product2.stock, 5)
        self.assertEqual(product3.stock, 4)

    def test_update_details_invalid(self):
        product = sample_product(name="product 1", stock=10)
        order = Order.objects.create()
        payload = [
            {"product": product, "cuantity": 3},
        ]
        order.add_details(payload)
        payload_to_update = [
            {"product": product, "cuantity": 200},
        ]
        current_details = order.details.all()
        try:
            order.update_details(payload_to_update, current_details)
        except ValidationError:
            self.assertRaises(ValidationError)
