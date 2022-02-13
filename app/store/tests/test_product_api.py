from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from store.models import Product
from store.api.serializers import ProductSerializer


PRODUCT_URL = reverse('store:product-list')


def detail_url(product_id):
    return reverse('store:product-detail', args=[product_id])


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def sample_product(**params):
    defaults = {
        "name": "sample product",
        "stock": 20,
        "price": 100.00
    }

    defaults.update(params)
    return Product.objects.create(**defaults)


class PrivateProductApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'password'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_products(self):
        sample_product()
        sample_product()

        res = self.client.get(PRODUCT_URL)

        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_view_product_detail(self):
        product = sample_product()
        url = detail_url(product.id)
        res = self.client.get(url)
        serializer = ProductSerializer(product)
        self.assertEqual(res.data, serializer.data)

    def test_create_product_successful(self):
        payload = {"name": "Product", "price": 200.00, "stock": 30}
        self.client.post(PRODUCT_URL, payload)

        exists = Product.objects.filter(name=payload['name']).exists()
        self.assertTrue(exists)

    def test_create_product_invalid(self):
        payload = {"name": "", "price": 200, "stock": ''}
        res = self.client.post(PRODUCT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_product(self):
        product = sample_product()
        payload = {"name": "new product", "price": 200.00, "stock": 5}
        url = detail_url(product.id)
        self.client.patch(url, payload)
        product.refresh_from_db()
        self.assertEqual(product.name, payload['name'])

    def test_full_update_product(self):
        product = sample_product()
        payload = {"name": "new product", "price": 200.00, "stock": 5}
        url = detail_url(product.id)
        self.client.put(url, payload)

        product.refresh_from_db()
        self.assertEqual(product.name, payload['name'])
        self.assertEqual(product.price, payload['price'])
        self.assertEqual(product.stock, payload['stock'])

    def test_set_stock(self):
        product = sample_product(stock=10)
        url = reverse("store:set_stock", args=[product.id])
        self.client.put(url, {"stock": 20}, format='json')
        product.refresh_from_db()
        self.assertEqual(product.stock, 20)
