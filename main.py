from collections import defaultdict
import time
import re

from src.bot_utils import create_temp_directory, send_ipfs_notification, jail_check, dict_to_md_list, \
    message_upload_to_ipfs, base_keyboard_reply_markup
from src.lcd_utils import validators_state, search_cid
from src.bash_utils import create_cyberlink, create_account, transfer_tokens
from config import CYBER_KEY_NAME, BASE_MENU_LOWER, MONITORING_MENU_LOWER, TWEETER_MENU_LOWER, MONITORING_KEYBOARD, \
    TWEETER_KEYBOARD, TWEET_HASH, AVATAR_HASH, FOLLOW_HASH, DEV_MODE, States, bot, db_worker, CYBERPAGE_URL, \
    CYBERPAGE_BASE_URL, TOKEN_NAME, COMMAND_LIST, SUPPORT_ACCOUNT, logging

# Create directory for temporary files
create_temp_directory()

# Drop tables
# db_worker.drop_all_tables()

# Create tables
db_worker.create_all_tables()

# Create dictionaries
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
        reply_markup=base_keyboard_reply_markup(message.from_user.id))


@bot.message_handler(commands=['start'])
def start_message(message):
    state[message.chat.id] = States.S_START
    # TODO Update message text
    bot.send_message(
        message.chat.id,
        'Hello {}!\nI can create cyberLinks, upload content to IPFS and check monitor validator jail status.'.format(
            message.from_user.username),
        reply_markup=base_keyboard_reply_markup(message.from_user.id))


@bot.message_handler(
    func=lambda message: state[message.chat.id] == States.S_UPLOAD_IPFS,
    content_types=['audio', 'contact', 'document', 'location', 'photo', 'video', 'video_note', 'voice'])
@bot.message_handler(
    func=lambda message: (state[message.chat.id] == States.S_UPLOAD_IPFS) \
                         & (message.text is None or message.text.lower() not in BASE_MENU_LOWER),
    content_types=['text'])
def upload_to_ipfs(message):
    ipfs_hash, error = message_upload_to_ipfs(message)
    send_ipfs_notification(message=message,
                           ipfs_hash=ipfs_hash,
                           error=error,
                           add_ipfs=True)


@bot.message_handler(
    func=lambda message: state[message.chat.id] == States.S_SEARCH,
    content_types=['audio', 'contact', 'document', 'location', 'photo', 'video', 'video_note', 'voice'])
@bot.message_handler(
    func=lambda message: (state[message.chat.id] == States.S_SEARCH)
                         & (message.text is None or message.text.lower() not in BASE_MENU_LOWER),
    content_types=['text'])
def search(message, number_of_search_results: int = 5):
    ipfs_hash, error = message_upload_to_ipfs(message)
    send_ipfs_notification(message=message,
                           ipfs_hash=ipfs_hash,
                           error=error,
                           message_text='',
                           add_ipfs=True)
    if ipfs_hash:
        search_list, search_error = search_cid(ipfs_hash)
        if search_list:
            search_list = search_list[:min(len(search_list), number_of_search_results)]
            message_text = f'Top {number_of_search_results} search results:\n' + ''.join(
                f'<u><a href="https://ipfs.io/ipfs/{item["cid"]}">{item["cid"]}</a></u>\n' for item in search_list) + \
                f'\nother results on the <u><a href="{CYBERPAGE_BASE_URL}/search/{ipfs_hash}">cyb.ai</a></u>'
        elif search_error == 'CID not found':
            message_text = 'The content identifier not found in the cyber graph'
        else:
            message_text = search_error
        bot.send_message(
            message.chat.id,
            message_text,
            parse_mode='HTML',
            reply_markup=base_keyboard_reply_markup(message.from_user.id))
    bot.send_message(
        message.chat.id,
        'Please send other <u>search request</u> as text, file, photo, video, audio, '
        'IPFS hash, URL, contact, location, video or voice',
        parse_mode="HTML",
        reply_markup=base_keyboard_reply_markup(message.from_user.id))


@bot.message_handler(
    func=lambda message: (state[message.chat.id] == States.S_STARTPOINT_CYBERLINK) &
                         (((message.content_type == 'text') & (
                                 message.text is None or message.text.lower() not in BASE_MENU_LOWER))
                          | (message.content_type in ('audio', 'contact', 'document', 'location',
                                                      'photo', 'video', 'video_note', 'voice'))),
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
    func=lambda message: (state[message.chat.id] == States.S_ENDPOINT_CYBERLINK) &
                         (((message.content_type == 'text') & (
                                 message.text is None or message.text.lower() not in BASE_MENU_LOWER))
                          | (message.content_type in ('audio', 'contact', 'document', 'location',
                                                      'photo', 'video', 'video_note', 'voice'))),
    content_types=['audio', 'contact', 'document', 'location', 'photo', 'text', 'video', 'video_note', 'voice'])
def endpoint_cyberlink(message):
    ipfs_hash, ipfs_error = message_upload_to_ipfs(message)
    send_ipfs_notification(message, ipfs_hash, ipfs_error, message_text='')
    if ipfs_hash is None:
        return
    elif ipfs_hash == cyberlink_startpoint_ipfs_hash[message.chat.id]:
        bot.send_message(
            message.chat.id,
            'From and To CID is equal.\n<u>Cannot create cyberLink to self beginning</u>.',
            parse_mode='HTML',
            reply_markup=base_keyboard_reply_markup(message.from_user.id))
        logging.info(
            f"cyberLink was not created, from {cyberlink_startpoint_ipfs_hash[message.chat.id]}, to {ipfs_hash}. "
            f"Self cyberlink")
    elif ipfs_hash:
        cyberlink_hash, cyberlink_error = \
            create_cyberlink(
                account_name=db_worker.get_account_name(message.from_user.id),
                from_hash=cyberlink_startpoint_ipfs_hash[message.chat.id],
                to_hash=ipfs_hash)
        if cyberlink_error and cyberlink_startpoint_ipfs_hash[message.chat.id] not in (TWEET_HASH, FOLLOW_HASH,
                                                                                       AVATAR_HASH):
            cyberlink_hash, cyberlink_error = \
                create_cyberlink(
                    account_name=CYBER_KEY_NAME,
                    from_hash=cyberlink_startpoint_ipfs_hash[message.chat.id],
                    to_hash=ipfs_hash)
        if cyberlink_hash:
            bot.send_message(
                message.chat.id,
                f'cyberlink has been created in the transaction: '
                f'<u><a href="{CYBERPAGE_URL}/tx/{cyberlink_hash}">{cyberlink_hash}</a></u> \n',
                parse_mode='HTML',
                reply_markup=base_keyboard_reply_markup(message.from_user.id))
            bot.send_message(
                message.chat.id,
                f'from: <u><a href="https://ipfs.io/ipfs/{cyberlink_startpoint_ipfs_hash[message.chat.id]}">'
                f'{cyberlink_startpoint_ipfs_hash[message.chat.id]}</a></u>\n'
                f'to: <u><a href="https://ipfs.io/ipfs/{ipfs_hash}">{ipfs_hash}</a></u>',
                parse_mode='HTML',
                reply_markup=base_keyboard_reply_markup(message.from_user.id))
            db_worker.write_cyberlink(
                user_id=message.from_user.id,
                cyberlink_hash=cyberlink_hash,
                from_ipfs_hash=cyberlink_startpoint_ipfs_hash[message.chat.id],
                to_ipfs_hash=ipfs_hash)
            if db_worker.get_cyberlink_count(user_id=message.from_user.id) == 10:
                bot.send_message(
                    message.chat.id,
                    f'Congratulations!\n'
                    f'You have created 10 links.',
                    reply_markup=base_keyboard_reply_markup(message.from_user.id))
        elif cyberlink_error and cyberlink_startpoint_ipfs_hash[message.chat.id] in (TWEET_HASH, AVATAR_HASH,
                                                                                     FOLLOW_HASH):
            bot.send_message(
                message.chat.id,
                f"You don't have personal bandwidth and "
                f"you cannot create cyberlink from `avatar`, `follow` and `tweet` CID by cyberdBot account\n"
                f"Please get <u>A</u> and <u>V</u> coins before creating cyberlink",
                reply_markup=base_keyboard_reply_markup(message.from_user.id))
        elif cyberlink_error:
            bot.send_message(
                message.chat.id,
                f'CyberLink has not been created',
                reply_markup=base_keyboard_reply_markup(message.from_user.id))
    state[message.chat.id] = States.S_STARTPOINT_CYBERLINK
    bot.send_message(
        message.chat.id,
        'Please enter a keyword as a starting point for a new cyberLink or choose another service from the menu.\n'
        'You may enter an IPFS hash, URL, text, file, photo, video, audio, contact, location, video or voice.\n'
        'Please enter a keyword by which your content will be searchable in cyber, this will create the first part '
        'of the cyberlink.\n'
        'Please remember to be gentle, the search is case-sensitive.',
        reply_markup=base_keyboard_reply_markup(message.from_user.id))


@bot.message_handler(
    func=lambda message: (((message.content_type == 'text')
                           & (message.text is None or message.text.lower() not in list(
                                set().union(TWEETER_MENU_LOWER, BASE_MENU_LOWER).difference(['tweet']))))
                          | (message.content_type in ('audio', 'contact', 'document', 'location',
                                                      'photo', 'video', 'video_note', 'voice')))
                         & (state[message.chat.id] == States.S_NEW_TWEET),
    content_types=['audio', 'contact', 'document', 'location', 'photo', 'text', 'video', 'video_note', 'voice'])
def add_tweet(message):
    ipfs_hash, ipfs_error = message_upload_to_ipfs(message, lower_transform=False)
    send_ipfs_notification(message, ipfs_hash, ipfs_error, message_text='')
    if ipfs_hash == TWEET_HASH:
        bot.send_message(
            message.chat.id,
            f'It is not possible to post the word <u>tweet</u>',
            parse_mode="HTML",
            reply_markup=TWEETER_KEYBOARD)
        logging.info(
            f"cyberLink for tweet has not been created, from {cyberlink_startpoint_ipfs_hash[message.chat.id]}, "
            f"to {ipfs_hash}. Self cyberlink")
    elif db_worker.get_account_name(message.from_user.id) == '':
        bot.send_message(
            message.chat.id,
            f'You have not signed up, please sign up and get <u>A</u> and <u>V</u> coins before tweeting',
            parse_mode="HTML",
            reply_markup=TWEETER_KEYBOARD)
    elif ipfs_hash:
        cyberlink_hash, cyberlink_error = \
            create_cyberlink(
                account_name=db_worker.get_account_name(message.from_user.id),
                from_hash=TWEET_HASH,
                to_hash=ipfs_hash)
        if cyberlink_error == 'not enough personal bandwidth':
            bot.send_message(
                message.chat.id,
                f'Tweet has not been created\n'
                f'You have not enough personal bandwidth, please get <u>A</u> and <u>V</u> coins before tweeting',
                reply_markup=TWEETER_KEYBOARD)
            return
        elif cyberlink_hash:
            bot.send_message(
                message.chat.id,
                f'Tweet created: <u><a href="{CYBERPAGE_BASE_URL}/ipfs/{ipfs_hash}/meta">{ipfs_hash}</a></u>\n'
                f'cyberLink in the transaction: <u><a href="{CYBERPAGE_URL}/tx/{cyberlink_hash}">{cyberlink_hash}</a>'
                f'</u>\n',
                parse_mode='HTML',
                reply_markup=TWEETER_KEYBOARD)
            db_worker.write_cyberlink(
                user_id=message.from_user.id,
                cyberlink_hash=cyberlink_hash,
                from_ipfs_hash=TWEET_HASH,
                to_ipfs_hash=ipfs_hash)
            if db_worker.get_cyberlink_count(user_id=message.from_user.id) == 10:
                bot.send_message(
                    message.chat.id,
                    f'Congratulations!\n'
                    f'You have created 10 links',
                    reply_markup=TWEETER_KEYBOARD)
        elif cyberlink_error:
            bot.send_message(
                message.chat.id,
                f'Tweet has not been created\n',
                reply_markup=TWEETER_KEYBOARD)
    bot.send_message(
        message.chat.id,
        'Please send new tweet as text, file, photo, video, audio, IPFS hash, URL, contact, location, '
        'video or voice',
        reply_markup=TWEETER_KEYBOARD)


@bot.message_handler(
    func=lambda message: state[message.chat.id] == States.S_START,
    content_types=['audio', 'contact', 'document', 'location', 'photo', 'video', 'video_note', 'voice'])
def send_message_when_start_state(message):
    bot.send_message(
        message.chat.id,
        'Please press "Create cyberLink" or the "Upload to IPFS" button to upload this file',
        reply_markup=base_keyboard_reply_markup(message.from_user.id))


@bot.message_handler(commands=COMMAND_LIST)
@bot.message_handler(
    func=lambda message: (message.text.lower() in BASE_MENU_LOWER),
    content_types=['text']
)
def main_menu(message):
    state[message.chat.id] = States.S_START

    if message.text.lower() in ['jail check', '/check']:
        jail_check(message.chat.id)

    elif message.text.lower() in ['validator list', '/validators']:
        validators_dict, _ = validators_state()
        bot.send_message(
            message.chat.id,
            '{}'.format(dict_to_md_list(validators_dict)),
            parse_mode="HTML",
            reply_markup=base_keyboard_reply_markup(message.from_user.id))

    elif message.text.lower() == 'jail check settings':
        state[message.chat.id] = States.S_MONITORING
        bot.send_message(
            message.chat.id,
            'Enter a validator moniker',
            reply_markup=MONITORING_KEYBOARD)

    elif message.text.lower() in ['search', '/search']:
        state[message.chat.id] = States.S_SEARCH
        bot.send_message(
            message.chat.id,
            'Please send <u>search request</u> as text, file, photo, video, audio, '
            'IPFS hash, URL, contact, location, video or voice',
            parse_mode="HTML",
            reply_markup=base_keyboard_reply_markup(message.from_user.id))

    elif message.text.lower() in ['upload to ipfs', '/ipfs']:
        state[message.chat.id] = States.S_UPLOAD_IPFS
        bot.send_message(
            message.chat.id,
            'Please send text, file, photo, video, audio, IPFS hash, URL, contact, location, video or voice',
            reply_markup=base_keyboard_reply_markup(message.from_user.id))

    elif message.text.lower() in ['create cyberlink', '/cyberlink']:
        if db_worker.check_sign_user(message.from_user.id):
            state[message.chat.id] = States.S_STARTPOINT_CYBERLINK
            bot.send_message(
                message.chat.id,
                'Please enter a keyword as a starting point for a new cyberLink or choose another service from the '
                'menu.\n'
                'You may enter an text, cyberLink, IPFS hash, URL, file, photo, video, audio, contact, location, video '
                'or voice.\n'
                'Please enter a keyword by which your content will be searchable in cyber, this will create '
                'the first part of the cyberLink.\n'
                'Please remember to be gentle, the search is case-sensitive.',
                reply_markup=base_keyboard_reply_markup(message.from_user.id))
        else:
            bot.send_message(
                message.chat.id,
                'Please create an account before creating cyberLinks',
                reply_markup=base_keyboard_reply_markup(message.from_user.id))

    elif message.text.lower() == 'sign up':
        if db_worker.check_sign_user(message.from_user.id):
            bot.send_message(
                message.chat.id,
                f'You already created account',
                reply_markup=base_keyboard_reply_markup(message.from_user.id))
            return
        state[message.chat.id] = States.S_SIGNUP
        bot.send_message(
            message.chat.id,
            f'To the maximum extent permitted by law, we make no guarantee, representation or warranty and expressly '
            f'disclaim liability (whether to you or any person).\n'
            f'Your use of this bot and addresses created by the bot is voluntary and at your sole risk.\n'
            f'In the event of any loss, hack or theft of tokens from your account, you acknowledge and '
            f'confirm that you shall have no right(s), claim(s) or causes of action in any way whatsoever against us.',
            reply_markup=base_keyboard_reply_markup(message.from_user.id))
        bot.send_message(
            message.chat.id,
            'Choose a name for your cyber account. Remember that the name will be case sensitive',
            reply_markup=base_keyboard_reply_markup(message.from_user.id))

    elif message.text.lower() in ['tweet', '/tweet']:
        if not db_worker.check_sign_user(message.from_user.id):
            bot.send_message(
                message.chat.id,
                f'For tweet please sign up',
                reply_markup=base_keyboard_reply_markup(message.from_user.id))
            return
        state[message.chat.id] = States.S_NEW_TWEET
        bot.send_message(
            message.chat.id,
            'Please send new tweet as text, file, photo, video, audio, IPFS hash, URL, contact, location, '
            'video or voice',
            reply_markup=TWEETER_KEYBOARD)

    elif message.text.lower() in ['/issue']:
        bot.send_message(
            message.chat.id,
            f'You can report an issue or suggest improvements in '
            f'<u><a href="https://github.com/Snedashkovsky/cyberdBot/issues">the cyberdBot repository</a></u>.\n'
            f'Also you can text to @{SUPPORT_ACCOUNT} directly.',
            parse_mode="HTML",
            reply_markup=base_keyboard_reply_markup(message.from_user.id))


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
            reply_markup=base_keyboard_reply_markup(message.from_user.id))


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
    if len(account_name) > 20:
        bot.send_message(
            message.chat.id,
            'Your account name contains more than 20 characters.\n'
            'Please enter a different account name.',
            reply_markup=base_keyboard_reply_markup(message.from_user.id))
        return
    if re.match("^[A-Za-z0-9_-]*$", account_name):
        account_data, create_account_error = create_account(account_name)
    else:
        bot.send_message(
            message.chat.id,
            'Your account name should only contain letters and numbers.\n'
            'Please enter a different account name.',
            reply_markup=base_keyboard_reply_markup(message.from_user.id))
        return
    if account_data:
        try:
            db_worker.signup_user(message.from_user.id, account_data["name"], account_data["address"])
        except Exception as e:
            logging.error(f'Error in adding new user to DB: {e}')
        bot.send_message(
            message.chat.id,
            f'Account: <b>{account_data["name"]}</b>\n'
            f'Address: <u><a href="{CYBERPAGE_URL}/contract/{account_data["address"]}">{account_data["address"]}</a>'
            f'</u>\n'
            f'Mnemonic phrase: <u>{account_data["mnemonic_phrase"]}</u>\n'
            f'**Important** Please write down your mnemonic phrase and keep it safe. '
            f'The mnemonic is the only way to recover your account. '
            f'There is no way of recovering any funds if you lose it.',
            parse_mode="HTML",
            reply_markup=base_keyboard_reply_markup(message.from_user.id))
    else:
        bot.send_message(
            message.chat.id,
            f'Account not created',
            reply_markup=base_keyboard_reply_markup(message.from_user.id))


@bot.message_handler(
    func=lambda message: ((message.content_type == 'text')
                          & (message.text is None or message.text.lower() in TWEETER_MENU_LOWER))
                         & (state[message.chat.id] == States.S_NEW_TWEET),
    content_types=['text'])
def tweet_menu(message):
    if message.text.lower() == TWEETER_MENU_LOWER[0]:
        bot.send_message(
            message.chat.id,
            'Please send new tweet as text, file, photo, video, audio, IPFS hash, URL, contact, location, '
            'video or voice',
            reply_markup=TWEETER_KEYBOARD)
    elif message.text.lower() == TWEETER_MENU_LOWER[1]:
        state[message.chat.id] = States.S_START
        bot.send_message(
            message.chat.id,
            'Main Menu',
            reply_markup=base_keyboard_reply_markup(message.from_user.id))


if __name__ == '__main__':

    if DEV_MODE:
        print('DEV_MODE')
        bot.polling(
            none_stop=True,
            timeout=100)
    else:
        # Handler to avoid disconnection
        while True:
            try:
                bot.polling(
                    none_stop=True,
                    timeout=100)
            except Exception as e:
                logging.error(f'Error in the main: {e}. Restart in 15 sec')
                # restart in 15 sec
                time.sleep(15)
