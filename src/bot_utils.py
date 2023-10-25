from requests import get
from json import dumps
from os import mkdir
import re
from telebot.apihelper import ApiTelegramException, ApiException

from src.lcd_utils import validators_state
from src.ipfs_utils import upload_text, upload_file
from config import BASE_KEYBOARD, BASE_AFTER_SIGN_UP_KEYBOARD, TELEBOT_TOKEN, CYBERPAGE_BASE_URL, db_worker, bot, \
    logging


def base_keyboard_reply_markup(user_id: int):
    if db_worker.check_sign_user(user_id):
        return BASE_AFTER_SIGN_UP_KEYBOARD
    return BASE_KEYBOARD


def create_temp_directory():
    try:
        mkdir('temp')
    except OSError:
        logging.info('Creation of the directory "temp" failed. Maybe directory already exists.')
    else:
        logging.info('Successfully created the directory "temp".')


def dict_to_md_list(input_dict: dict):
    srt_from_dict = ''''''
    for key in sorted(list(input_dict.keys())):
        if input_dict[key] == 'jailed':
            srt_from_dict += f'''- <u><b>{key}: {input_dict[key]} </b></u>\n'''
            pass
        else:
            srt_from_dict += f'''- {key}: {input_dict[key]}\n'''
    return str(srt_from_dict)


def jail_check(chat_id: int, pressed_button=True):
    moniker_list = db_worker.get_moniker(chat_id)
    moniker_list = moniker_list if moniker_list != [''] else []
    if len(moniker_list) > 0:
        validators_dict, _ = validators_state()
        monikers_in_validator_list = [moniker for moniker in moniker_list if moniker in validators_dict.keys()]
        monikers_not_in_validator_list = [moniker for moniker in moniker_list if moniker not in validators_dict.keys()]
        # Send message only about inactive state during automatic jail check and all states in other cases
        if not pressed_button:
            moniker_dict = {moniker: validators_dict[moniker] for moniker in monikers_in_validator_list
                            if validators_dict[moniker] != 'Active'}
        else:
            moniker_dict = {moniker: validators_dict[moniker] for moniker in monikers_in_validator_list}
        try:
            if len(moniker_dict.keys()) > 0:
                bot.send_message(
                    chat_id,
                    dict_to_md_list(moniker_dict),
                    parse_mode='HTML',
                    reply_markup=base_keyboard_reply_markup(chat_id),
                    timeout=5)
            if len(monikers_not_in_validator_list) > 0:
                bot.send_message(
                    chat_id,
                    dict_to_md_list({moniker: 'not in validator list' for moniker in monikers_not_in_validator_list}),
                    parse_mode='HTML',
                    reply_markup=base_keyboard_reply_markup(chat_id),
                    timeout=5)
                logging.warning(f"{monikers_not_in_validator_list} monikers not in validators list")
        except (ApiException, ApiTelegramException) as error_send_message:
            logging.error(
                f"The message was not sent. Chat id {chat_id} Error {error_send_message}")
        except KeyError as error_moniker_key:
            logging.error(
                f"One Moniker in {moniker_list} not in validators list. Chat id {chat_id} Error {error_moniker_key}")
    elif pressed_button:
        bot.send_message(
            chat_id,
            'Please set a validator moniker in the `Jail check settings` so I can check it',
            reply_markup=base_keyboard_reply_markup(chat_id))


def download_file_from_telegram(message, file_id):
    try:
        file_info = bot.get_file(file_id)
    except ApiException as file_info_exception:
        logging.error(file_info_exception)
        bot.send_message(
            message.chat.id,
            'Please upload a file smaller than 20 MB',
            reply_markup=base_keyboard_reply_markup(message.from_user.id))
        return
    response = get('https://api.telegram.org/file/bot{0}/{1}'.format(TELEBOT_TOKEN, file_info.file_path))
    file_path = 'temp/' + file_id
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return file_path
    return


def message_upload_to_ipfs(message, lower_transform: bool = True):
    if message.content_type == 'text':
        # TODO add conditions for checking IPFS Hash
        if re.match('^[A-Za-z0-9]{46}$', message.text.strip()):
            return message.text.strip(), None
        elif lower_transform and len(message.text) < 46:
            return upload_text(message.text.lower())
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


def send_ipfs_notification(message, ipfs_hash: str, error: str, message_text: str = 'other content',
                           add_ipfs: bool = False):
    if ipfs_hash:
        bot.send_message(
            message.chat.id,
            f'{str(message.content_type).capitalize()} successfully uploaded\n'
            f'IPFS Hash: <u><a href="{CYBERPAGE_BASE_URL}/oracle/ask/{ipfs_hash}">{ipfs_hash}</a></u>',
            parse_mode='HTML',
            reply_markup=base_keyboard_reply_markup(message.from_user.id))
        if message_text:
            bot.send_message(
                message.chat.id,
                f'Please send {message_text}.\n'
                f'You may send an text, cyberLink, {"" if add_ipfs else "IPFS hash, "}URL, file, photo, video, audio, '
                f'contact, location, video or voice.',
                reply_markup=base_keyboard_reply_markup(message.from_user.id))
    elif error:
        bot.send_message(
            message.chat.id,
            f'{str(message.content_type).capitalize()} not uploaded.\n'
            f'Error: {error}\n'
            f'Please send {message_text}.\n'
            f'You may send an text, cyberLink, {"" if add_ipfs else "IPFS hash, "}URL, file, photo, video, audio, '
            f'contact, location, video or voice.',
            reply_markup=base_keyboard_reply_markup(message.from_user.id))
