import requests

from config import IPFS_HOST, logging


def upload_text(text: str):
    logging.info(f'Uploading text: {text}')
    try:
        files = {
            'file': ('text', text)
        }
        response = requests.post(f'{IPFS_HOST}/api/v0/add', files=files)
        return response.json()['Hash'], None
    except Exception as upload_error:
        logging.error(upload_error)
        return None, upload_error


def upload_file(file_name: str):
    logging.info(f'Uploading file: {file_name}')
    try:
        files = {
            'file': ('file_name', open(file_name, 'rb'))
        }
        response = requests.post(f'{IPFS_HOST}/api/v0/add', files=files)
        return response.json()['Hash'], None
    except Exception as upload_error:
        logging.error(upload_error)
        return None, upload_error
