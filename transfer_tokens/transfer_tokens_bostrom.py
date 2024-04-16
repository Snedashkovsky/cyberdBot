
import json
import pandas as pd
from time import sleep
from cyberpy import address_to_address
from telebot.apihelper import ApiTelegramException

from src.bash_utils import transfer_tokens
from config import BASE_AFTER_SIGN_UP_KEYBOARD, db_worker, bot, TOKEN_NAME, CYBERPAGE_URL, CYBERPAGE_BASE_URL, \
    CYBER_CHAIN_ID


TRANSFER_VALUE_NEW_USERS = 10_000_000
TRANSFER_VALUE_LEADERS = 100_000_000
MILLIAMPERE_TRANSFER_VALUE = 1_000
MILLIVOLT_TRANSFER_VALUE = 1_000
MILLIAMPERE_TOKEN_NAME = 'MILLIAMPERE'
MILLIVOLT_TOKEN_NAME = 'MILLIVOLT'
TOCYB_TOKEN_NAME = 'TOCYB'
TOTAL_GOL_GIFT = 1_178_234_463
NEW_USER_MESSAGE = ''
GENESIS_PATH = '../data/genesis_bostrom.json'


def message_genesis(bostrom_address: str, genesis_balance: int) -> str:
    return f'''
Your address <b><a href="{CYBERPAGE_URL}/contract/{bostrom_address}/wallet">{bostrom_address}</a></b> ({address_to_address(address=bostrom_address, prefix='cyber')}) was included in the {CYBER_CHAIN_ID} Genesis.
The genesis balance is <b>{round(genesis_balance/1e6)} M{TOKEN_NAME}</b> and <b>{round(genesis_balance/1e6)} M{TOCYB_TOKEN_NAME}</b>.'''


def message_transfer(transfer_value: float, address: str = '', links_amount: int = 0, token_for_links_amount: float = 0,
                     users_message: str = '', token_name: str = TOKEN_NAME) -> str:
    if token_name == TOKEN_NAME and links_amount >= 1:
        return f'''
@cyberdBot received 1,178 M{TOKEN_NAME} and 1,178 M{TOCYB_TOKEN_NAME} from Game of Link and distributes this prize between accounts in proportion to the number of created cyberLinks.
You created {int(links_amount):>,} cyberLinks.
<b>{round(transfer_value / 1e6, 1)} M{TOKEN_NAME}</b> and <b>{token_for_links_amount} M{TOCYB_TOKEN_NAME}</b> has been transferred to your address <u><a href="{CYBERPAGE_URL}/contract/{address}">{address}</a></u>, including <b>{token_for_links_amount} M{TOKEN_NAME}</b> reward for cyberLink creation.
Let's delegate, investmint to Volt and Ampere by <a href="{CYBERPAGE_BASE_URL}/halloffame">cyb.ai/halloffame</a> and <a href="https://github.com/chainapsis/keplr-extension">Keplr</a>.
{users_message}'''
    elif token_name == TOKEN_NAME:
        return f'''
@cyberdBot transferred <b>{int(transfer_value // 1e6)} M{token_name}</b> to your address <u><a href="{CYBERPAGE_URL}/contract/{address}">{address}</a></u>.
Let's delegate, investmint to Volt and Ampere by <a href="{CYBERPAGE_BASE_URL}/halloffame">cyb.ai/halloffame</a> and <a href="https://github.com/chainapsis/keplr-extension">Keplr</a>.'''
    elif token_name == MILLIAMPERE_TOKEN_NAME:
        return f'''
Also @cyberdBot transferred <b>{int(transfer_value // 1e3)} {token_name[5:]}</b> to you.
AMPERE token will give weight to your cyberLinks.'''
    elif token_name == MILLIVOLT_TOKEN_NAME:
        return f'''
@cyberdBot transferred <b>{int(transfer_value // 1e3)} {token_name[5:]}</b> to you.
Your bandwidth can be enough to generate at least <b>1 link per day</b>.
Let's tweet and create cyberLinks by @cyberdBot or <a href="{CYBERPAGE_BASE_URL}">cyb.ai</a>.
Go for it!'''
    elif token_name == TOCYB_TOKEN_NAME:
        return ''


def send_message_genesis(row: pd.Series) -> bool:
    if row.genesis_balance:
        print(f'\nSend genesis message to {row.user_id} with {row.genesis_balance} genesis bostrom address {row.address}')
        try:
            bot.send_message(
                chat_id=row.user_id,
                text=message_genesis(bostrom_address=row.address, genesis_balance=row.genesis_balance),
                parse_mode='HTML',
                reply_markup=BASE_AFTER_SIGN_UP_KEYBOARD)
            return True
        except ApiTelegramException:
            print('Chat not found')
            return False
    return True


def send_message_transfer(row: pd.Series, transfer_value: int, gift_per_link: float,
                          token_name: str = TOKEN_NAME, user_message: str = '') -> None:
    if token_name == TOCYB_TOKEN_NAME:
        print(f'\nSend transfer message to user_id {row.user_id}, link number {row.number_of_cyberlinks}, address '
              f'{row.address}, transfer value {transfer_value:>,}{token_name.lower()}')
        return
    elif token_name in (MILLIAMPERE_TOKEN_NAME, MILLIVOLT_TOKEN_NAME):
        message_text = \
             message_transfer(transfer_value=transfer_value, token_name=token_name)
    elif row.number_of_cyberlinks > 0:
        message_text = \
            message_transfer(
                transfer_value=transfer_value,
                links_amount=row.number_of_cyberlinks,
                address=row.address,
                token_for_links_amount=round(row.number_of_cyberlinks * gift_per_link / 1e6, 1),
                users_message=user_message)
    else:
        message_text = \
            message_transfer(transfer_value=transfer_value, address=row.address)
    print(f'\nSend transfer message to user_id {row.user_id}, link number {row.number_of_cyberlinks}, address '
          f'{row.address}, transfer value {transfer_value:>,}{token_name.lower()}')
    try:
        bot.send_message(
            chat_id=row.user_id,
            text=message_text,
            parse_mode='HTML',
            reply_markup=BASE_AFTER_SIGN_UP_KEYBOARD)
    except ApiTelegramException:
        print('Chat not found')


def send_info_message(row: pd.Series) -> bool:
    try:
        bot.send_message(
            chat_id=row.user_id,
            text=f'To the maximum extent permitted by law, we make no guarantee, representation or warranty and '
                 f'expressly disclaim liability (whether to you or any person).\n'
                 f'Your use of this bot and accounts created by the bot is voluntary and at your sole risk.\n'
                 f'In the event of any loss, hack or theft of tokens from your account, you acknowledge and '
                 f'confirm that you shall have no right(s), claim(s) or causes of action in any way whatsoever against '
                 f'us.\n'
                 f'<b>Strongly recommended moving your tokens to an account created without @cyberdBot<b>, for example,'
                 f' using <a href="https://github.com/chainapsis/keplr-extension">Keplr</a> or native '
                 f'<a href="https://github.com/cybercongress/go-cyber">CLI</a>.\n'
                 f'@cyberdBot sent the mnemonic phrase for the address during sign up, you can use it to get access.',
            parse_mode='HTML',
            reply_markup=BASE_AFTER_SIGN_UP_KEYBOARD)
        return True
    except ApiTelegramException:
        print('Chat not found')
        return False


def get_users_and_links() -> pd.DataFrame:
    return db_worker.get_df(
        query='''
            SELECT
                acc.user_id,
                acc.account_name,
                links.cyberlink_count,
                acc.account_address
            FROM (
                SELECT
                    user_id,
                    account_name,
                    account_address
                FROM accounts
                WHERE account_address != ''
                ) as acc
            LEFT JOIN (
                SELECT
                    user_id,
                    count() as cyberlink_count
                FROM (
                    SELECT distinct
                        user_id,
                        from_ipfs_hash,
                        to_ipfs_hash
                    FROM cyberlinks
                    WHERE ts < '2021-06-12 00:00:00')
                GROUP BY user_id
                ORDER BY cyberlink_count DESC
                ) as links
            ON links.user_id = acc.user_id
            ORDER BY links.cyberlink_count DESC''',
        columns=['user_id', 'account_name', 'number_of_cyberlinks', 'address']).fillna(0)


def get_boot_genesis_balances(genesis_path: str = GENESIS_PATH) -> dict:

    def _get_boot(coins: list) -> int:
        for coin in coins:
            if coin['denom'] == 'boot':
                return int(coin['amount'])
        return 0

    with open(genesis_path) as f:
        genesis_json = json.load(f)
    return {item['address'].lower(): _get_boot(item['coins']) for item in genesis_json["app_state"]['bank']['balances']}


def compute_users_and_links() -> pd.DataFrame:
    _users_and_links_df = get_users_and_links()
    _genesis_balances_dict = get_boot_genesis_balances()
    _users_and_links_df['genesis_balance'] = _users_and_links_df.address.map(
        lambda x: _genesis_balances_dict[x] if x in _genesis_balances_dict.keys() else 0)
    return _users_and_links_df


def transfer_tokens_handler(row: pd.Series, transfer_value: int, gift_per_link: float = 0, token_name: str = TOKEN_NAME,
                            send_message: bool = True, sleep_time: float = 4) -> bool:
    sleep(sleep_time)
    _transfer_success, _transfer_error = \
        transfer_tokens(
            account_address=row.address,
            value=transfer_value,
            token_name=token_name)
    if _transfer_success and send_message:
        send_message_transfer(
            row=row,
            transfer_value=transfer_value,
            gift_per_link=gift_per_link,
            token_name=token_name)
        return True
    elif _transfer_success:
        return True
    else:
        print(f'\nUnsuccessful transfer {transfer_value} {token_name} to {row.address}, user id {row.user_id}')
        return False


def run():

    users_and_links_df = compute_users_and_links()
    total_cyberlinks = int(sum(users_and_links_df.number_of_cyberlinks))
    gift_per_link = round(TOTAL_GOL_GIFT/sum(users_and_links_df.number_of_cyberlinks))
    print(f'Total cyberLinks created by cyberdBot {total_cyberlinks:>,}\n'
          f'Gift per created cyberLink {gift_per_link:>,} {TOKEN_NAME}')

    for df_index in users_and_links_df.index:

        row = users_and_links_df.iloc[df_index].copy()
        token_amount = TRANSFER_VALUE_LEADERS if row.number_of_cyberlinks >= 10 else TRANSFER_VALUE_NEW_USERS
        transfer_value = token_amount + row.number_of_cyberlinks * gift_per_link
        genesis_message_status = send_message_genesis(row=row)
        if genesis_message_status:
            transfer_tokens_handler(row=row, transfer_value=transfer_value, gift_per_link=gift_per_link)
            transfer_tokens_handler(row=row, transfer_value=transfer_value, gift_per_link=gift_per_link,
                                    token_name=TOCYB_TOKEN_NAME)
            if df_index <= 56:
                transfer_tokens_handler(row=row, transfer_value=MILLIAMPERE_TRANSFER_VALUE,
                                        token_name=MILLIAMPERE_TOKEN_NAME)
                transfer_tokens_handler(row=row, transfer_value=MILLIVOLT_TRANSFER_VALUE,
                                        token_name=MILLIVOLT_TOKEN_NAME)
            send_info_message(row=row)

    print('Transferred Successfully!')


if __name__ == '__main__':
    run()
