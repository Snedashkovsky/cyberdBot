import requests

from config import IPFS_HOST


def upload_text(text):
    print(f'Uploading text: {text}')
    try:
        files = {
            'file': ('text', text)
        }
        response = requests.post(f'{IPFS_HOST}/api/v0/add', files=files)
        return response.json()['Hash'], None
    except Exception as upload_error:
        print(upload_error)
        return None, upload_error


def upload_files(file_name):
    print(f'Uploading file: {file_name}')
    try:
        files = {
            'file': ('file_name', open(file_name, 'rb'))
        }
        response = requests.post(f'{IPFS_HOST}/api/v0/add', files=files)
        return response.json()['Hash'], None
    except Exception as upload_error:
        print(upload_error)
        return None, upload_error


def upload_image(file_name):
    print(file_name)
    pass
    return


def upload_video(file_name):
    print(file_name)
    pass
    return


def upload_voice(file_name):
    print(file_name)
    pass
    return
