from requests import get
from telebot import apihelper
from json import dumps

from src.extract_state import validators_state
from src.ipfs_utils import upload_text, upload_file
from config import BASE_KEYBOARD, TELEBOT_TOKEN, db_worker, bot


def dict_to_md_list(input_dict):
    srt_from_dict = ''''''
    for key in sorted(list(input_dict.keys())):
        if input_dict[key] == 'jailed':
            srt_from_dict += f'''- <u><b>{key}: {input_dict[key]} </b></u>\n'''
            pass
        else:
            srt_from_dict += f'''- {key}: {input_dict[key]}\n'''
    return str(srt_from_dict)


def jail_check(chat_id):
    moniker_list = db_worker.get_moniker(chat_id)
    moniker_list = moniker_list if moniker_list != [''] else []
    if len(moniker_list) > 0:
        validators_dict = validators_state()
        bot.send_message(
            chat_id,
            dict_to_md_list({key: validators_dict[key] for key in moniker_list}),
            parse_mode='HTML',
            reply_markup=BASE_KEYBOARD)
    else:
        bot.send_message(
            chat_id,
            'Please send validator moniker for check it',
            reply_markup=BASE_KEYBOARD)


def download_file_from_telegram(message, file_id):
    try:
        file_info = bot.get_file(file_id)
    except apihelper.ApiException as file_info_exception:
        print(file_info_exception)
        bot.send_message(
            message.chat.id,
            'Please upload file less than 20 MB',
            reply_markup=BASE_KEYBOARD)
        return
    response = get('https://api.telegram.org/file/bot{0}/{1}'.format(TELEBOT_TOKEN, file_info.file_path))
    file_path = 'temp/' + file_id
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return file_path
    return


def message_upload_to_ipfs(message):
    if message.content_type == 'text':
        # TODO add condition for check IPFS Hash
        if len(message.text) == 46:
            return message.text, None
        return upload_text(message.text)
    elif message.content_type in ('audio', 'video', 'video_note', 'voice'):
        file_id = message.json[message.content_type]['file_id']
    elif message.content_type == 'document':
        file_id = message.document.file_id
    elif message.content_type in ('location', 'contact'):
        # TODO change location and contact format for more convenient
        return upload_text(dumps(message.json[message.content_type]))
    elif message.content_type == 'photo':
        file_id = message.json['photo'][-1]['file_id']
    else:
        return None, None
    file_path = download_file_from_telegram(message, file_id)
    if file_path:
        return upload_file(file_path)
    return None, None


def send_ipfs_notification(message, ipfs_hash, error, message_text='other content'):
    if ipfs_hash:
        bot.send_message(
            message.chat.id,
            f'{str(message.content_type).capitalize()} successfully uploaded\n'
            f'IPFS Hash: <u>{ipfs_hash}</u>\n'
            f'IPFS Link: https://ipfs.io/ipfs/{ipfs_hash}\n',
            parse_mode='HTML',
            reply_markup=BASE_KEYBOARD)
        if message_text:
            bot.send_message(
                message.chat.id,
                f'Please send {message_text}.\n'
                f'You may send ipfs hash, url, text, file, photo, video, audio, contact, location, video note and voice.',
                reply_markup=BASE_KEYBOARD)
    elif error:
        bot.send_message(
            message.chat.id,
            f'{str(message.content_type).capitalize()} not uploaded.\n'
            f'Error: {error}\n'
            f'Please send other content.\n'
            f'You may send ipfs hash, url, text, file, photo, video, audio, contact, location, video note and voice.',
            reply_markup=BASE_KEYBOARD)
