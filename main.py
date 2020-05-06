from collections import defaultdict
import time
from os import mkdir

from src.bot_utils import send_ipfs_notification, jail_check, dict_to_md_list, message_upload_to_ipfs
from src.bash_utils import validators_state, create_cyberlink
from config import BASE_MENU_LOWER, MONITORING_MENU_LOWER, BASE_KEYBOARD, MONITORING_KEYBOARD, DEV_MODE, States, bot, \
    db_worker

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
cyberlink_startpoint_ipfs_hash = defaultdict(lambda: None, key='some_value')


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


@bot.message_handler(commands=['start'])
def start_message(message):
    state[message.chat.id] = States.S_START
    # TODO Update message text
    bot.send_message(
        message.chat.id,
        'Hello {}!\nI can create cyberLinks, upload content to IPFS and check monitor validator jail status.'.format(
            message.from_user.username),
        reply_markup=BASE_KEYBOARD)


@bot.message_handler(
    func=lambda message: state[message.chat.id] == States.S_UPLOAD_IPFS,
    content_types=['audio', 'contact', 'document', 'location', 'photo', 'video', 'video_note', 'voice'])
def files_upload_to_ipfs(message):
    ipfs_hash, error = message_upload_to_ipfs(message)
    send_ipfs_notification(message, ipfs_hash, error)


@bot.message_handler(
    func=lambda message: state[message.chat.id] == States.S_STARTPOINT_CYBERLINK,
    content_types=['audio', 'contact', 'document', 'location', 'photo', 'text', 'video', 'video_note', 'voice'])
def startpoint_cyberlink(message):
    ipfs_hash, error = message_upload_to_ipfs(message)
    send_ipfs_notification(message, ipfs_hash, error, message_text='endpoint of cyberLink')
    if ipfs_hash:
        cyberlink_startpoint_ipfs_hash[message.chat.id] = ipfs_hash
        state[message.chat.id] = States.S_ENDPOINT_CYBERLINK


@bot.message_handler(
    func=lambda message: state[message.chat.id] == States.S_ENDPOINT_CYBERLINK,
    content_types=['audio', 'contact', 'document', 'location', 'photo', 'text', 'video', 'video_note', 'voice'])
def endpoint_cyberlink(message):
    ipfs_hash, ipfs_error = message_upload_to_ipfs(message)
    send_ipfs_notification(message, ipfs_hash, ipfs_error, message_text=None)
    if ipfs_hash:
        state[message.chat.id] = States.S_STARTPOINT_CYBERLINK
        cyberlink_hash, cyberlink_error = create_cyberlink(cyberlink_startpoint_ipfs_hash[message.chat.id], ipfs_hash)
        if cyberlink_hash:
            bot.send_message(
                message.chat.id,
                f'CyberLink created: https://cyber.page/network/euler/tx/{cyberlink_hash} \n'
                f'Transaction hash: <u>{cyberlink_hash}</u> ',
                parse_mode='HTML',
                reply_markup=BASE_KEYBOARD)
            bot.send_message(
                message.chat.id,
                f'from: https://ipfs.io/ipfs/{cyberlink_startpoint_ipfs_hash[message.chat.id]}\n'
                f'to: https://ipfs.io/ipfs/{ipfs_hash}',
                parse_mode='HTML',
                reply_markup=BASE_KEYBOARD)
        elif cyberlink_error:
            bot.send_message(
                message.chat.id,
                f'CyberLink not created\n'
                f'error: {cyberlink_error}',
                reply_markup=BASE_KEYBOARD)
        bot.send_message(
            message.chat.id,
            'Please enter a keyword as a starting point for a new cyberLink or choose another service from the menu.\n'
            'You may enter an IPFS hash, URL, text, file, photo, video, audio, contact, location, video or voice.\n'
            'Please enter a keyword by which your content will be searchable in cyber, this will create the first part '
            'of the cyberlink.\n'
            'Please remember to be gentle, the search is case-senstive.',
            reply_markup=BASE_KEYBOARD)


@bot.message_handler(
    func=lambda message: state[message.chat.id] == States.S_START,
    content_types=['audio', 'contact', 'document', 'location', 'photo', 'video', 'video_note', 'voice'])
def send_message_when_start_state(message):
    bot.send_message(
        message.chat.id,
        'Please press "Create cyberLink" or the "Upload to IPFS" button to upload this file',
        reply_markup=BASE_KEYBOARD)


@bot.message_handler(
    func=lambda message: (message.text.lower() not in BASE_MENU_LOWER) \
                         & (state[message.chat.id] == States.S_UPLOAD_IPFS),
    content_types=['text'])
def text_upload_to_ipfs(message):
    ipfs_hash, error = message_upload_to_ipfs(message)
    send_ipfs_notification(message, ipfs_hash, error)


@bot.message_handler(
    func=lambda message: (message.text.lower() in BASE_MENU_LOWER) \
                         & (state[message.chat.id] in (States.S_START, States.S_STARTPOINT_CYBERLINK,
                                                       States.S_ENDPOINT_CYBERLINK, States.S_UPLOAD_IPFS)),
    content_types=['text']
)
def main_menu(message):
    state[message.chat.id] = States.S_START
    if message.text.lower() == 'jail check':
        jail_check(message.chat.id)
    elif message.text.lower() == 'validator list':
        validators_dict, _ = validators_state()
        bot.send_message(
            message.chat.id,
            '{}'.format(dict_to_md_list(validators_dict)),
            parse_mode="HTML",
            reply_markup=BASE_KEYBOARD)
    elif message.text.lower() == 'jail check settings':
        state[message.chat.id] = States.S_MONITORING
        bot.send_message(
            message.chat.id,
            'Enter a validator moniker',
            reply_markup=MONITORING_KEYBOARD)
    elif message.text.lower() == 'upload to ipfs':
        state[message.chat.id] = States.S_UPLOAD_IPFS
        bot.send_message(
            message.chat.id,
            'Please send URL, text, file, photo, video, audio, contact, location, video or voice',
            reply_markup=BASE_KEYBOARD)
    elif message.text.lower() == 'create cyberlink':
        state[message.chat.id] = States.S_STARTPOINT_CYBERLINK
        bot.send_message(
            message.chat.id,
            'Please enter a keyword as a starting point for a new cyberLink or choose another service from the menu.\n'
            'You may enter an text, cyberLink, IPFS hash, URL, file, photo, video, audio, contact, location, video or '
            'voice.\n'
            'Please enter a keyword by which your content will be searchable in cyber, this will create the first part '
            'of the cyberLink.\n'
            'Please remember to be gentle, the search is case-senstive.',
            reply_markup=BASE_KEYBOARD)


@bot.message_handler(
    func=lambda message: (message.text.lower() in MONITORING_MENU_LOWER) \
                         & (state[message.chat.id] == States.S_MONITORING),
    content_types=['text']
)
def monitoring_menu(message):
    if message.text.lower() == 'add validator moniker':
        bot.send_message(
            message.chat.id,
            'Enter a validator moniker',
            reply_markup=MONITORING_KEYBOARD)
    elif message.text.lower() == 'jail check':
        jail_check(message.chat.id)
    elif message.text.lower() == 'reset validator moniker':
        db_worker.reset_moniker(message.chat.id)
        bot.send_message(
            message.chat.id,
            'Moniker reset. Please add a validators moniker to check their jailed status',
            reply_markup=MONITORING_KEYBOARD)
    elif message.text.lower() == 'validator list':
        validators_dict, _ = validators_state()
        bot.send_message(
            message.chat.id,
            '{}'.format(dict_to_md_list(validators_dict)),
            parse_mode="HTML",
            reply_markup=MONITORING_KEYBOARD)
    elif message.text.lower() == 'hourly check':
        scheduler_state = db_worker.get_scheduler_state(message.chat.id)
        if scheduler_state == 0:
            db_worker.set_scheduler_state(message.chat.id, 1)
            bot.send_message(
                message.chat.id,
                'Set hourly jail check',
                reply_markup=MONITORING_KEYBOARD)
            jail_check(message.chat.id)
            bot.send_message(
                message.chat.id,
                'The following notifications will be sent to you hourly',
                reply_markup=MONITORING_KEYBOARD)
        else:
            db_worker.set_scheduler_state(message.chat.id, 0)
            bot.send_message(
                message.chat.id,
                'Unset hourly jail check',
                reply_markup=MONITORING_KEYBOARD)
    elif message.text.lower() == 'back to main':
        state[message.chat.id] = States.S_START
        bot.send_message(
            message.chat.id,
            'Back to main menu',
            reply_markup=BASE_KEYBOARD)


@bot.message_handler(
    func=lambda message: (message.text.lower() not in MONITORING_MENU_LOWER) \
                         & (state[message.chat.id] == States.S_MONITORING),
    content_types=['text'])
def add_validator_moniker(message):
    moniker = message.text
    moniker_list = db_worker.get_moniker(message.chat.id)
    validators_dict, _ = validators_state()

    if moniker in moniker_list:
        bot.send_message(
            message.chat.id,
            'This moniker has already been added',
            reply_markup=MONITORING_KEYBOARD)
        jail_check(message.chat.id)
    elif moniker in validators_dict.keys():
        db_worker.add_moniker(message.chat.id, moniker)
        bot.send_message(
            message.chat.id,
            'The moniker has been added',
            reply_markup=MONITORING_KEYBOARD)
        jail_check(message.chat.id)
    else:
        bot.send_message(
            message.chat.id,
            'The moniker you have entered is not in the validator list. Please enter a valid moniker and be gentle, '
            'the bot is case sensitive',
            reply_markup=MONITORING_KEYBOARD)


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
