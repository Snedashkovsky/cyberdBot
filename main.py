from collections import defaultdict
import time
from os import mkdir

from src.bot_utils import send_ipfs_notification, jail_check, dict_to_md_list, message_upload_to_ipfs
from src.bash_utils import validators_state, create_cyberlink, create_account, transfer_eul_tokens
from config import CYBERD_KEY_NAME, BASE_MENU_LOWER, MONITORING_MENU_LOWER, BASE_KEYBOARD, MONITORING_KEYBOARD, \
    DEV_MODE, States, bot, db_worker

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
# db_worker.drop_table_accounts()
# db_worker.drop_table_cyberlinks()
# Create tables
db_worker.create_table_monikers()
db_worker.create_table_scheduler()
db_worker.create_table_accounts()
db_worker.create_table_cyberlinks()

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
    send_ipfs_notification(message=message,
                           ipfs_hash=ipfs_hash,
                           error=error,
                           add_ipfs=True)


@bot.message_handler(
    func=lambda message: (((message.content_type == 'text') and (message.text.lower() not in BASE_MENU_LOWER)) or \
                          (message.content_type in ('audio', 'contact', 'document', 'location',
                                                    'photo', 'video', 'video_note', 'voice'))) \
                         and (state[message.chat.id] == States.S_STARTPOINT_CYBERLINK),
    content_types=['text', 'audio', 'contact', 'document', 'location', 'photo', 'video', 'video_note', 'voice'])
def startpoint_cyberlink(message):
    ipfs_hash, error = message_upload_to_ipfs(message)
    send_ipfs_notification(message=message,
                           ipfs_hash=ipfs_hash,
                           error=error,
                           message_text='an endpoint for your cyberlink. The endpoint is the content itself')
    if ipfs_hash:
        cyberlink_startpoint_ipfs_hash[message.chat.id] = ipfs_hash
        state[message.chat.id] = States.S_ENDPOINT_CYBERLINK


@bot.message_handler(
    func=lambda message: (((message.content_type == 'text') and (message.text.lower() not in BASE_MENU_LOWER)) or \
                          (message.content_type in ('audio', 'contact', 'document', 'location',
                                                    'photo', 'video', 'video_note', 'voice'))) \
                         & (state[message.chat.id] == States.S_ENDPOINT_CYBERLINK),
    content_types=['audio', 'contact', 'document', 'location', 'photo', 'text', 'video', 'video_note', 'voice'])
def endpoint_cyberlink(message):
    ipfs_hash, ipfs_error = message_upload_to_ipfs(message)
    send_ipfs_notification(message, ipfs_hash, ipfs_error, message_text=None)
    if ipfs_hash:
        state[message.chat.id] = States.S_STARTPOINT_CYBERLINK
        cyberlink_hash, cyberlink_error = \
            create_cyberlink(
                account_name=db_worker.get_account_name(message.from_user.id),
                from_hash=cyberlink_startpoint_ipfs_hash[message.chat.id],
                to_hash=ipfs_hash)
        if cyberlink_error=='not enough personal bandwidth':
            cyberlink_hash, cyberlink_error = \
                create_cyberlink(
                    account_name=CYBERD_KEY_NAME,
                    from_hash=cyberlink_startpoint_ipfs_hash[message.chat.id],
                    to_hash=ipfs_hash)
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
            db_worker.write_cyberlink(
                user_id=message.from_user.id,
                cyberlink_hash=cyberlink_hash,
                from_ipfs_hash=cyberlink_startpoint_ipfs_hash[message.chat.id],
                to_ipfs_hash=ipfs_hash)
            if db_worker.get_cyberlink_count(user_id=message.from_user.id) == 10:
                transfer_state, transfer_error = transfer_eul_tokens(
                    account_address=db_worker.get_account_address(user_id=message.from_user.id),
                    value=7_500_000)
                if transfer_state:
                    bot.send_message(
                        message.chat.id,
                        'Congratulations!\n'
                        'You have created 10 links.\n'
                        '7,500,000 EUL Tokens have been transferred to your account!',
                        reply_markup=BASE_KEYBOARD)
                else:
                    bot.send_message(
                        message.chat.id,
                        f'Tokens was not transferred.\nError: {transfer_error}',
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
    send_ipfs_notification(message, ipfs_hash, error, add_ipfs=True)


@bot.message_handler(
    func=lambda message: (message.text.lower() in BASE_MENU_LOWER) \
                         & (state[message.chat.id] in (States.S_START, States.S_STARTPOINT_CYBERLINK,
                                                       States.S_ENDPOINT_CYBERLINK, States.S_UPLOAD_IPFS,
                                                       States.S_SIGNUP)),
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
        if db_worker.check_sign_user(message.from_user.id):
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
        else:
            bot.send_message(
                message.chat.id,
                'Please create an account before creating cyberLinks',
                reply_markup=BASE_KEYBOARD)
    elif message.text.lower() == 'sign up':
        if db_worker.check_sign_user(message.from_user.id):
            bot.send_message(
                message.chat.id,
                f'You already created account',
                reply_markup=BASE_KEYBOARD)
            return
        if message.from_user.id > 836000000:
            bot.send_message(
                message.chat.id,
                f'Your telegram was recently registered, please use an older account',
                reply_markup=BASE_KEYBOARD)
            return
        state[message.chat.id] = States.S_SIGNUP
        bot.send_message(
            message.chat.id,
            'To the maximum extent permitted by law, we make no guarantee, representation or warranty and expressly '
            'disclaim liability (whether to you or any person).\n'
            'Your use of this bot is voluntary and at your sole risk.\n'
            'In the event of any loss, hack or theft of EUL tokens from your account, you acknowledge and confirm '
            'that you shall have no right(s), claim(s) or causes of action in any way whatsoever against us.',
            reply_markup=BASE_KEYBOARD)
        bot.send_message(
            message.chat.id,
            'Choose a name for your cyber account. Remember that the name will be case sensitive',
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
            bot.send_message(
                message.chat.id,
                'The following notifications will be sent to you hourly',
                reply_markup=MONITORING_KEYBOARD)
            jail_check(message.chat.id)
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
            'Main Menu',
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
            'The moniker you have entered is not in the validator list.\n'
            'Please enter a valid moniker and be gentle, the bot is case sensitive',
            reply_markup=MONITORING_KEYBOARD)


@bot.message_handler(
    func=lambda message: (message.text.lower() not in BASE_MENU_LOWER) \
                         & (state[message.chat.id] == States.S_SIGNUP),
    content_types=['text'])
def sign_up_user(message):
    account_name = message.text
    account_data, create_account_error = create_account(account_name)
    if account_data:
        try:
            db_worker.signup_user(message.from_user.id, account_data["name"], account_data["address"])
        except Exception as e:
            print(e)
        bot.send_message(
            message.chat.id,
            f'Account: <b>{account_data["name"]}</b>\n'
            f'Address: <b>{account_data["address"]}</b>\n\n'
            f'Mnemonic phrase: <u>{account_data["mnemonic_phrase"]}</u>\n'
            f'**Important**Please write down your mnemonic phrase and keep it safe. '
            f'The mnemonic is the only way to recover your account. '
            f'There is no way of recovering any funds if you lose it.',
            parse_mode="HTML",
            reply_markup=BASE_KEYBOARD)
        transfer_state, transfer_error = transfer_eul_tokens(account_data["address"])
        if transfer_state:
            bot.send_message(
                message.chat.id,
                'I have transferred 2,500,000 EUL to you account.\n'
                'You can create cyberlinks now!\n'
                'If you create more than 10 cyberlinks, I will transfer an additional 7,500,000 EUL to your account!',
                reply_markup=BASE_KEYBOARD)
        else:
            bot.send_message(
                message.chat.id,
                f'Tokens was not transferred.\nError: {transfer_error}',
                reply_markup=BASE_KEYBOARD)
    else:
        bot.send_message(
            message.chat.id,
            f'Account not created\n'
            f'error: {create_account_error}',
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
