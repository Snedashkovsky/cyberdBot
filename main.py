from telebot import TeleBot, apihelper
from collections import defaultdict
import time
from requests import get
from json import dumps
from os import mkdir

from src.extract_state import validators_state
from config import TELEBOT_TOKEN, DB_FILE, BASE_MENU_LOWER, BASE_KEYBOARD, DEV_MODE, States
from src.sql_utils import SQLighter
from src.ipfs_utils import upload_text, upload_file

bot = TeleBot(TELEBOT_TOKEN)
db_worker = SQLighter(DB_FILE)

# Create directory for temporary files
try:
    mkdir('temp')
except OSError:
    print('Creation of the directory "temp" failed. Maybe directory already exists.')
else:
    print('Successfully created the directory "temp".')

# Drop tables
# db_worker.drop_table_monikers()
# db_worker.drop_table_scheduler()
# Create tables
db_worker.create_table_monikers()
db_worker.create_table_scheduler()

state = defaultdict(lambda: States.S_START, key='some_value')


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


@bot.message_handler(
    content_types=['new_chat_members', 'left_chat_member', 'new_chat_title', 'new_chat_photo', 'delete_chat_photo',
                   'group_chat_created', 'supergroup_chat_created', 'channel_chat_created', 'migrate_to_chat_id',
                   'migrate_from_chat_id', 'pinned_message'])
def pass_unsupported_content_types(message):
    pass


@bot.message_handler(content_types=['sticker'])
def chat_unsupported_content_types(message):

    bot.send_message(
        message.chat.id,
        f'Unsupported message type: {message.content_type}',
        reply_markup=BASE_KEYBOARD)


@bot.message_handler(
    content_types=['audio', 'contact', 'document', 'location', 'photo', 'video', 'video_note', 'voice'])
def files_upload_to_ipfs(message):
    if state[message.chat.id] == States.S_START:
        bot.send_message(
            message.chat.id,
            'Please press "Upload to IPFS" button for upload this file to IPFS',
            reply_markup=BASE_KEYBOARD)
        return
    if message.content_type in ('audio', 'video', 'video_note', 'voice'):
        file_id = message.json[message.content_type]['file_id']
    elif message.content_type == 'document':
        file_id = message.document.file_id
    elif message.content_type in ('location', 'contact'):
        # TODO change location and contact format for more convenient
        ipfs_hash, error = upload_text(dumps(message.json[message.content_type]))
        send_ipfs_notification(message, ipfs_hash, error)
        return
    elif message.content_type == 'photo':
        file_id = message.json['photo'][-1]['file_id']
    else:
        return
    file_path = download_file_from_telegram(message, file_id)
    if file_path:
        ipfs_hash, error = upload_file(file_path)
        send_ipfs_notification(message, ipfs_hash, error)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id,
        'Hello {}! Please add a validator moniker'.format(message.from_user.username),
        reply_markup=BASE_KEYBOARD)


@bot.message_handler(
    func=lambda message: (message.text.lower() not in BASE_MENU_LOWER) \
                         & (state[message.chat.id] == States.S_UPLOAD_IPFS),
    content_types=['text'])
def text_upload_to_ipfs(message):
    ipfs_hash, error = upload_text(message.text)
    send_ipfs_notification(message, ipfs_hash, error)


@bot.message_handler(
    func=lambda message: message.text.lower() in BASE_MENU_LOWER,
    content_types=['text']
)
def main_menu(message):
    state[message.chat.id] = States.S_START
    if message.text.lower() == 'add validator moniker':
        bot.send_message(
            message.chat.id,
            'Enter a validator moniker',
            reply_markup=BASE_KEYBOARD)
    elif message.text.lower() == 'jail check':
        jail_check(message.chat.id)
    elif message.text.lower() == 'reset validator moniker':
        db_worker.reset_moniker(message.chat.id)
        bot.send_message(
            message.chat.id,
            'Moniker reset. Please add a validators moniker to check jailed status',
            reply_markup=BASE_KEYBOARD)
    elif message.text.lower() == 'validator list':
        validators_dict = validators_state()
        bot.send_message(
            message.chat.id,
            '{}'.format(dict_to_md_list(validators_dict)),
            parse_mode="HTML",
            reply_markup=BASE_KEYBOARD)
    elif message.text.lower() == 'hourly check':
        scheduler_state = db_worker.get_scheduler_state(message.chat.id)
        if scheduler_state == 0:
            db_worker.set_scheduler_state(message.chat.id, 1)
            bot.send_message(
                message.chat.id,
                'Set hourly jail check',
                reply_markup=BASE_KEYBOARD)
            jail_check(message.chat.id)
            bot.send_message(
                message.chat.id,
                'The following node status notifications will be sent to you hourly',
                reply_markup=BASE_KEYBOARD)
        else:
            db_worker.set_scheduler_state(message.chat.id, 0)
            bot.send_message(
                message.chat.id,
                'Unset hourly jail check',
                reply_markup=BASE_KEYBOARD)
    elif message.text.lower() == 'upload to ipfs':
        state[message.chat.id] = States.S_UPLOAD_IPFS
        bot.send_message(
            message.chat.id,
            'Please send text, file, photo, video, audio, contact, location, video note and voice',
            reply_markup=BASE_KEYBOARD)


@bot.message_handler(
    func=lambda message: (message.text.lower() not in BASE_MENU_LOWER) & (state[message.chat.id] == States.S_START),
    content_types=['text'])
def add_validator_moniker(message):
    moniker = message.text
    moniker_list = db_worker.get_moniker(message.chat.id)
    validators_dict = validators_state()

    if moniker in moniker_list:
        bot.send_message(
            message.chat.id,
            'The moniker already added',
            reply_markup=BASE_KEYBOARD)
        jail_check(message.chat.id)
    elif moniker in validators_dict.keys():
        db_worker.add_moniker(message.chat.id, moniker)
        bot.send_message(
            message.chat.id,
            'The moniker has been added',
            reply_markup=BASE_KEYBOARD)
        jail_check(message.chat.id)
    else:
        bot.send_message(
            message.chat.id,
            'The moniker you have entered is not in the list. Please enter a valid moniker and be gentle, the bot is '
            'case sensitive',
            reply_markup=BASE_KEYBOARD)


if __name__ == '__main__':

    if DEV_MODE:
        print('DEV_MODE')
        bot.polling(none_stop=True)
    else:
        # Handler to avoid disconnection
        while True:
            try:
                bot.polling(none_stop=True)
            except Exception as e:
                print(e)
                # restart in 15 sec
                time.sleep(15)
