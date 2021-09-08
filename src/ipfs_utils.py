from requests import post

from src.bash_utils import restart_ipfs_node
from config import IPFS_HOST, logging


def upload_text(text: str):
    logging.info(f'Uploading text: {text}')
    try:
        files = {
            'file': ('text', text)
        }
        response = post(f'{IPFS_HOST}/api/v0/add', files=files)
        return response.json()['Hash'], None
    except Exception as upload_error:
        if str(upload_error).find('Max retries exceeded') > -1:
            restart_ipfs_node()
        logging.error(upload_error)
        return None, upload_error


def upload_file(file_name: str):
    logging.info(f'Uploading file: {file_name}')
    try:
        files = {
            'file': ('file_name', open(file_name, 'rb'))
        }
        response = post(f'{IPFS_HOST}/api/v0/add', files=files)
        return response.json()['Hash'], None
    except Exception as upload_error:
        if str(upload_error).find('Max retries exceeded') > -1:
            restart_ipfs_node()
        logging.error(upload_error)
        return None, upload_error
