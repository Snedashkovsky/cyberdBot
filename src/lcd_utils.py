from requests import get

from config import LCD_HOST, logging
from cachetools.func import ttl_cache


@ttl_cache(maxsize=128, ttl=10)
def validators_state(
        validators_query: str = '/cosmos/staking/v1beta1/validators',
        lcd_host: str = LCD_HOST,
        status_dict=None):

    if status_dict is None:
        status_dict = {True: 'Jailed', False: 'Active'}
    try:
        _response = get(lcd_host + validators_query).json()
        _validators_json = _response['validators']
        if len(_validators_json) > 0:
            return {item['description']['moniker']: status_dict[item['jailed']] for item in _validators_json}, None
    except Exception as error_validators_lcd:
        logging.error(
            f'Validator state was not got. Error {error_validators_lcd}')
        return None, f'Validator state was not got. Error {error_validators_lcd}'
    return None, f'Validator state was not got. Please try to get it manually {lcd_host + validators_query}'


@ttl_cache(maxsize=128, ttl=10)
def search_cid(
        cid: str,
        search_query: str = '/rank/search?cid=',
        lcd_host: str = LCD_HOST):

    try:
        _response = get(lcd_host + search_query + cid).json()
        if 'error' in _response.keys() and len(_response['error']) > 13 and _response['error'][-13:] == 'cid not found':
            return None, 'CID not found'
        elif 'error' in _response.keys():
            return None, _response['error']

        search_json = _response['result']['result']
        if len(search_json) > 0:
            return search_json, None
    except Exception as error_search_lcd:
        logging.error(
            f'Search query was not got. Error {error_search_lcd}')
        return None, f'Search query was not got. Error {error_search_lcd}'
    return None, f'CID not found. Please try to get it manually {lcd_host + search_query + cid}'
