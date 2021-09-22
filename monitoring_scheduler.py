import time

from src.bot_utils import jail_check
from config import SCHEDULER_TIME, DEV_MODE, db_worker, logging


# Create tables
db_worker.create_all_tables()


def check_send_messages():
    while True:
        chat_id_list = db_worker.get_all_scheduler_states()
        for chat_id in chat_id_list:
            jail_check(chat_id,  pressed_button=False)
        logging.info(f'Validators status sent for {len(chat_id_list)} users')
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
                logging.error(f'Error {e}. It will be restarting in 15 sec')
                time.sleep(15)
