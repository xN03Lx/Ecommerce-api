from django.test import TestCase
from store.utils import has_values, convert_string_to_decimal


class UtilsTests(TestCase):

    def test_has_values_is_true(self):
        items = [1, 2, 3]
        result = has_values(items)
        self.assertTrue(result)

    def test_has_values_is_false(self):
        items = []
        result = has_values(items)
        self.assertFalse(result)

    def test_convert_string_to_decimal(self):
        result = convert_string_to_decimal('200.00')
        self.assertAlmostEqual(result, 200.00)
