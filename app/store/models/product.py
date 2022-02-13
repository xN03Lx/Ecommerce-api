from django.db import models
from django.core.validators import MinValueValidator


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )

    def set_stock(self, new_value):
        self.stock = new_value
        self.save()

    def check_stock(self, cuantity):
        if cuantity <= self.stock:
            return True
