from unittest.mock import patch, Mock
from django.test import TestCase
from store.services import get_exchange_houses, get_dollar_blue


exchange_houses_sample = [
    {
        "casa": {
            "compra": "105,67",
            "venta": "111,67",
            "agencia": "349",
            "nombre": "Dolar Oficial",
            "variacion": "0,05",
            "ventaCero": "TRUE",
            "decimales": "2"
        }
    },
    {
        "casa": {
            "compra": "211,50",
            "venta": "214,50",
            "agencia": "310",
            "nombre": "Dolar Blue",
            "variacion": "-0,46",
            "ventaCero": "TRUE",
            "decimales": "2"
        }
    }
]


class ServicesTests(TestCase):

    @patch('store.services.requests.get')
    def test_getting_exchange_houses_when_response_is_ok(self, mock_get):

        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = exchange_houses_sample

        response = get_exchange_houses()
        self.assertIsNotNone(response)

    @patch('store.services.requests.get')
    def test_getting_exchange_houses_when_response_is_not_ok(self, mock_get):
        mock_get.return_value.ok = False
        response = get_exchange_houses()
        self.assertIsNone(response)

    @patch('store.services.get_exchange_houses')
    def test_get_dollar_blue_is_not_none(self, mock_exchange_houses):
        mock_exchange_houses.return_value = Mock()
        mock_exchange_houses.return_value.json. \
            return_value = exchange_houses_sample
        dollar_blue = get_dollar_blue()
        self.assertEqual(dollar_blue, exchange_houses_sample[1])

    @patch('store.services.get_exchange_houses')
    def test_get_dollar_blue_is_none(self, mock_exchange_houses):
        mock_exchange_houses.return_value = None
        dollar_blue = get_dollar_blue()
        self.assertIsNone(dollar_blue, exchange_houses_sample[1])
