import time

from src.bash_utils import validators_state
from src.bot_utils import base_keyboard_reply_markup, dict_to_md_list
from config import BASE_KEYBOARD, SCHEDULER_TIME, DEV_MODE, bot, db_worker


# Create tables
db_worker.create_all_tables()


def jail_check(chat_id):
    moniker = db_worker.get_moniker(chat_id)
    if len(moniker) > 0:
        validators_dict, _ = validators_state()
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
        print('DEV_MODE')
        check_send_messages()
    else:
        # Handler to avoid disconnection
        while True:
            try:
                check_send_messages()
            except Exception as e:
                print(e)
                # restart in 15 sec
                time.sleep(15)
