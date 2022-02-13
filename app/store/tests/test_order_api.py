from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from store.models import Product, Order

from store.api.serializers import OrderSerializer

ORDER_URL = reverse('store:order-list')


def detail_url(order_id):
    return reverse('store:order-detail', args=[order_id])


def sample_order():
    return Order.objects.create()


def sample_order_detail(product_id, cuantity):
    defaults = {'cuantity': cuantity, 'product': product_id}
    return defaults


def sample_product(**params):
    defaults = {'name': 'sample product', 'stock': 20, 'price': 100.00}

    defaults.update(params)
    return Product.objects.create(**defaults)


class PrivateOrderApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
                'test@test.com',
                'testpass'
        )
        self.client.force_authenticate(self.user)

    @patch('store.api.views.cache.get')
    def test_retrieve_orders(self, mock_get_dollar_blue):
        mock_get_dollar_blue.return_value = '217.00'
        sample_order()
        sample_order()
        res = self.client.get(ORDER_URL)
        order = Order.objects.all()
        serializer = OrderSerializer(order, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_order_with_details(self):
        sample_product()
        sample_product()
        payload = {'details': [{'product': 1, 'cuantity': 2},
                               {'product': 2, 'cuantity': 1}]}

        res = self.client.post(ORDER_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=res.data['id'])
        details = order.details.all()
        self.assertEqual(details.count(), 2)
        self.assertEqual(
            payload['details'][0]['product'],
            details[0].product.id
        )
        self.assertEqual(
            payload['details'][1]['product'],
            details[1].product.id
        )

    def test_order_get_total(self):
        sample_product(price=200.00)
        sample_product(price=100.00)
        payload = {'details': [{'product': 1, 'cuantity': 2},
                               {'product': 2, 'cuantity': 1}]}

        res = self.client.post(ORDER_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=res.data['id'])
        self.assertEqual(order.get_total, 500.00)

    @patch('store.models.orders.cache.get')
    def test_order_get_total_usd(self, dolar_blue_mock):
        dolar_blue_mock.return_value = '211,00'
        sample_product(price=200.00)
        sample_product(price=100.00)
        payload = {'details': [{'product': 1, 'cuantity': 2},
                               {'product': 2, 'cuantity': 1}]}

        res = self.client.post(ORDER_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=res.data['id'])
        self.assertEqual(order.get_total_usd, 2.37)

    def test_create_order_with_products_duplicate(self):
        sample_product()
        payload = {'details': [{'product': 1, 'cuantity': 2},
                               {'product': 1, 'cuantity': 1}]}

        res = self.client.post(ORDER_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_products_out_stock(self):
        sample_product(stock=2)
        sample_product(stock=5)
        payload = {'details': [{'product': 1, 'cuantity': 20},
                               {'product': 1, 'cuantity': 20}]}

        res = self.client.post(ORDER_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('store.api.views.cache.get')
    def test_full_update_order_details(self, mock_get_dollar_blue):
        mock_get_dollar_blue.return_value = '217.00'
        product1 = sample_product(stock=10)
        product2 = sample_product(stock=15)
        product3 = sample_product(stock=5)
        order = sample_order()
        order_details = [{'product': product1, 'cuantity': 3},
                         {'product': product2, 'cuantity': 5},
                         {'product': product3, 'cuantity': 1}]
        order.add_details(order_details)
        payload = {'details': [{'product': product1.id, 'cuantity': 1},
                               {'product': product2.id, 'cuantity': 10},
                               {'product': product3.id, 'cuantity': 1}]}

        url = detail_url(order.id)
        self.client.put(url, payload, format='json')
        details = order.details.all()
        self.assertEqual(
            details[0].cuantity,
            payload['details'][0]['cuantity']
        )
        self.assertEqual(details[0].product.stock, 9)
        self.assertEqual(
            details[1].cuantity,
            payload['details'][1]['cuantity']
        )
        self.assertEqual(details[1].product.stock, 5)
        self.assertEqual(
            details[2].cuantity,
            payload['details'][2]['cuantity']
        )
        self.assertEqual(details[2].product.stock, 4)

    @patch('store.api.views.cache.get')
    def test_full_update_or_create_order_details(self, mock_get_dollar_blue):
        mock_get_dollar_blue.return_value = '217.00'
        product1 = sample_product(stock=10)
        product2 = sample_product(stock=15)
        order = sample_order()
        order_details = [{'product': product1, 'cuantity': 2}]
        order.add_details(order_details)
        payload = {'details': [{'product': product1.id, 'cuantity': 10},
                               {'product': product2.id, 'cuantity': 10}]}

        url = detail_url(order.id)
        self.client.put(url, payload, format='json')
        details = order.details.all()
        self.assertEqual(
            details[0].cuantity,
            payload['details'][0]['cuantity']
        )
        self.assertEqual(details[0].product.stock, 0)
        self.assertEqual(
            details[1].cuantity,
            payload['details'][1]['cuantity'])
        self.assertEqual(details[1].product.stock, 5)
        self.assertEqual(details.count(), 2)

    @patch('store.api.views.cache.get')
    def test_full_update_order_details_product_out_stock(
        self,
        mock_get_dollar_blue
    ):
        mock_get_dollar_blue.return_value = '217.00'
        product1 = sample_product(stock=10)
        order = sample_order()
        order_details = [{'product': product1, 'cuantity': 2}]
        order.add_details(order_details)
        payload = {'details': [{'product': product1.id, 'cuantity': 100}]}
        url = detail_url(order.id)
        res = self.client.put(url, payload, format='json')
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)
