from typing import List
from decimal import Decimal


def select_for_update(model, pk):
    return model.objects \
                .select_for_update() \
                .get(pk=pk)


def has_values(values: List) -> bool:
    if (len(values) > 0):
        return True


def convert_string_to_decimal(string: str) -> Decimal:
    return Decimal(string.replace(',', '.'))
