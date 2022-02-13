import requests
from typing import List, Dict, Union
from .constants import DOLARSI_URL_API, DOLAR_BLUE_CODE


def get_exchange_houses() -> Union[List[Dict[str, str]], None]:
    url = DOLARSI_URL_API + '?type=valoresprincipales'
    response = requests.get(url)
    if response.ok:
        return response
    else:
        return None


def get_dollar_blue() -> Union[Dict[str, str], None]:
    response = get_exchange_houses()
    if response is not None:
        exchange_houses = response.json()
        for house in exchange_houses:
            if house['casa']['agencia'] == DOLAR_BLUE_CODE:
                return house
