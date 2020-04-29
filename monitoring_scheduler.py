from telebot import TeleBot
import time

from extract_state import validators_state
from config import TELEBOT_TOKEN, DB_FILE, BASE_KEYBOARD, SCHEDULER_TIME, DEV_MODE
from sql_utils import SQLighter


bot = TeleBot(TELEBOT_TOKEN)
db_worker = SQLighter(DB_FILE)

db_worker.create_table_monikers()
db_worker.create_table_scheduler()


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
    moniker = db_worker.get_moniker(chat_id)
    if len(moniker) > 0:
        validators_dict = validators_state()
        bot.send_message(
            chat_id,
            dict_to_md_list({key: validators_dict[key] for key in moniker}),
            parse_mode="HTML",
            reply_markup=BASE_KEYBOARD)


def check_send_messages():
    while True:
        chat_id_list = db_worker.get_all_scheduler_states()
        for chat_id in chat_id_list:
            jail_check(chat_id)
        time.sleep(SCHEDULER_TIME)


if __name__ == '__main__':

    if DEV_MODE:
        check_send_messages()
    # Handler to avoid disconnection
    while True:
        try:
            check_send_messages()
        except Exception as e:
            print(e)
            # restart in 15 sec
            time.sleep(15)
