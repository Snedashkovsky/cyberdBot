from telebot import TeleBot
from collections import defaultdict
import time

from src.extract_state import validators_state
from config import TELEBOT_TOKEN, DB_FILE, BASE_MENU_LOWER, BASE_KEYBOARD, DEV_MODE, States
from src.sql_utils import SQLighter
from src.ipfs_utils import upload_text

bot = TeleBot(TELEBOT_TOKEN)
db_worker = SQLighter(DB_FILE)

# db_worker.drop_table_monikers()
# db_worker.drop_table_scheduler()
db_worker.create_table_monikers()
db_worker.create_table_scheduler()

state = defaultdict(lambda: 0, key='some_value')


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
            parse_mode="HTML",
            reply_markup=BASE_KEYBOARD)
    else:
        bot.send_message(
            chat_id,
            'Please send validator moniker for check it',
            reply_markup=BASE_KEYBOARD)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id,
        'Hello {}! Please add a validator moniker'.format(message.from_user.username),
        reply_markup=BASE_KEYBOARD)


@bot.message_handler(
    func=lambda message: message.text.lower() in BASE_MENU_LOWER,
    content_types=['text'])
def main_menu(message):
    state[message.chat.id] = 0
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
    elif message.text.lower() == 'hourly jail check':
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
        state[message.chat.id] = 1
        bot.send_message(
            message.chat.id,
            'Please send content',
            reply_markup=BASE_KEYBOARD)

@bot.message_handler(
    func=lambda message: (message.text.lower() not in BASE_MENU_LOWER) & (state[message.chat.id] == States.S_START))
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


@bot.message_handler(content_types=['text'])
@bot.message_handler(
    func=lambda message: (message.text.lower() not in BASE_MENU_LOWER) \
                       & (state[message.chat.id] == States.S_UPLOAD_IPFS))
def upload_to_ipfs(message):

    ipfs_hash, error = upload_text(message.text)
    if ipfs_hash:
        bot.send_message(
            message.chat.id,
            f'Text successfully uploaded. IPFS Hash: {ipfs_hash}\nIPFS Link: https://ipfs.io/ipfs/{ipfs_hash}\nPlease send other content',
            reply_markup=BASE_KEYBOARD)
    else:
        bot.send_message(
            message.chat.id,
            f'Text not uploaded. Error: {error}\nPlease send other content',
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
