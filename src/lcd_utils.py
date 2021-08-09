from requests import get
import logging

from config import LCD_HOST
from cachetools.func import ttl_cache


@ttl_cache(maxsize=128, ttl=10)
def validators_state(
        validators_query: str = '/cosmos/staking/v1beta1/validators',
        lcd_host: str = LCD_HOST,
        status_dict: dict = {True: 'Jailed', False: 'Active'}):

    response = get(lcd_host + validators_query).json()
    try:
        validators_json = response['validators']
        if len(validators_json) > 0:
            return {item['description']['moniker']: status_dict[item['jailed']] for item in validators_json}, None
    except Exception as error_validators_lcd:
        logging.error(
            f"Validator state was not got. Error {error_validators_lcd}")
        return None, f"Validator state was not got. Error {error_validators_lcd}"
    return None, f'Validator state was not got. Please try to get it manually {lcd_host + validators_query}'
