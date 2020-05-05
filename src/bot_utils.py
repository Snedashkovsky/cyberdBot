from requests import get
from telebot import apihelper

from src.extract_state import validators_state
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


def send_ipfs_notification(message, ipfs_hash, error):
    if ipfs_hash:
        bot.send_message(
            message.chat.id,
            f'{message.content_type} successfully uploaded\nIPFS Hash: <u>{ipfs_hash}</u>\nIPFS Link: '
            f'https://ipfs.io/ipfs/{ipfs_hash}\nPlease send other content',
            parse_mode='HTML',
            reply_markup=BASE_KEYBOARD)
    else:
        bot.send_message(
            message.chat.id,
            f'{message.content_type} not uploaded.\nError: {error}\nPlease send other content',
            reply_markup=BASE_KEYBOARD)
