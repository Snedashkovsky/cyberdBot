import json
import numpy as np
import pandas as pd
from cyberpy import address_to_address
from telebot.apihelper import ApiTelegramException

from src.bash_utils import transfer_tokens, create_account
from config import BASE_AFTER_SIGN_UP_KEYBOARD, db_worker, bot, TOKEN_NAME, CYBERPAGE_URL, CYBERPAGE_BASE_URL, \
    CYBER_CHAIN_ID


TRANSFER_VALUE_NEW_USERS = 10_000_000
TRANSFER_VALUE_LEADERS = 100_000_000
MILLIAMPERE_TRANSFER_VALUE = 1_000
MILLIAMPERE_TOKEN_NAME = 'MILLIAMPERE'
TOTAL_GOL_GIFT = 1_178_234_463
LOAD_NEW_DATA = True
CREATE_NEW_ADDRESS_COLUMN = False
CREATE_NEW_ADDRESSES = False
NEW_USER_MESSAGE = f'If you create <b>10 links</b> with the bot, another <b>90 M{TOKEN_NAME}</b> will be transferred.'


def message_genesis(cyber_address: str, bostrom_address: str, genesis_balance: str) -> str:
    return f'''
Also your bostrom address <b>{bostrom_address}</b> was included in the {CYBER_CHAIN_ID} Genesis.
Your genesis balance is <b>{genesis_balance}</b>.
{CYBERPAGE_URL}/contract/{bostrom_address}/wallet
@cyberdBot sent the mnemonic phrase for the cyber address <b>{cyber_address}</b> during sign up.new_bostrom_address
You can use this mnemonic phrase to access the bostrom address by any wallet (e.g. Keplr).'''


def message_transfer_boot(transfer_value: int, address: str, token_name: str = TOKEN_NAME) -> str:
    return f'''
@cyberdBot transferred <b>{transfer_value} M{token_name}</b> to your address <u><a href="{CYBERPAGE_URL}/contract/{address}">{address}</a></u>.
Remember, these tokens shall not be migrated to the production network.
Let's delegate, investmint to Volt and Ampere by <a href="{CYBERPAGE_BASE_URL}/mint">cyb.ai/mint</a>.
{NEW_USER_MESSAGE}
Go for it!'''


def message_transfer_ampere(transfer_value: int, token_name: str = MILLIAMPERE_TOKEN_NAME) -> str:
    return f'''
Also @cyberdBot transferred <b>{transfer_value} {token_name}</b> to you.
These tokens shall not be migrated to the production network too.
Your bandwidth can be enough to generate at least <b>1 link per day</b>.
Let's tweet and create cyberLinks by @cyberdBot or <a href="{CYBERPAGE_BASE_URL}">cyb.ai</a>.
Go for it!'''


def message_transfer_with_links(transfer_value: float, links_amount: int, address: str,
                                token_for_links_amount: float, users_message: str) -> str:
    return f'''
@cyberdBot received 1,178 M{TOKEN_NAME} from Game of Link and distributes this prize between accounts in proportion to the number of created cyberLinks.
You created {int(links_amount):>,} cyberLinks.
<b>{transfer_value} M{TOKEN_NAME}</b> has been transferred to your address <u><a href="{CYBERPAGE_URL}/contract/{address}">{address}</a></u>, including <b>{token_for_links_amount} M{TOKEN_NAME}</b> reward for cyberLink creation.
Remember, these tokens shall not be migrated to the production network.
Let's delegate, investmint to Volt and Ampere by <a href="{CYBERPAGE_BASE_URL}/mint">cyb.ai/mint</a> and <a href="https://github.com/chainapsis/keplr-extension">Keplr wallet</a>.
{users_message}'''


def sign_up_user(user_id: int, account_name: str):
    account_data, create_account_error = create_account(account_name)
    if account_data:
        print(f'Account created {account_name} {user_id} {account_data["address"]}')
        try:
            bot.send_message(
                user_id,
                f'@cyberdBot created new account for you:\n'
                f'Account: <b>{account_data["name"]}</b>\n'
                f'Address: <b>{account_data["address"]}</b>\n'
                f'Link: {CYBERPAGE_URL}/contract/{account_data["address"]}\n\n'
                f'Mnemonic phrase: <u>{account_data["mnemonic_phrase"]}</u>\n'
                f'**Important**Please write down your mnemonic phrase and keep it safe. '
                f'The mnemonic is the only way to recover your account. '
                f'There is no way of recovering any funds if you lose it.\n'
                f'Storing tokens on this account is not secure and is intended for experimentation.',
                parse_mode="HTML",
                reply_markup=BASE_AFTER_SIGN_UP_KEYBOARD)
            return account_data["address"]
        except ApiTelegramException:
            print('Chat not found')
    else:
        print(f'Account not created, user id {user_id}. Error: {create_account_error}')
    return


def send_message_genesis(row: pd.Series) -> None:
    if len(row.genesis) > 0:
        print(f'\nSend genesis message to {row.user_id} with {row.genesis_str} genesis bostrom address {row.bostrom_address}')
        try:
            bot.send_message(
                chat_id=row.user_id,
                text=message_genesis(row.address, row.bostrom_address, row.genesis_str),
                parse_mode='HTML',
                reply_markup=BASE_AFTER_SIGN_UP_KEYBOARD)
        except ApiTelegramException:
            print('Chat not found')


def send_message_transfer(row: pd.Series, transfer_value: int, gift_per_link: float, new_bostrom_address: str = '', token_name: str = TOKEN_NAME) -> None:
    user_message = '' if row.number_of_cyberlinks >= 10 else NEW_USER_MESSAGE
    if token_name == MILLIAMPERE_TOKEN_NAME:
        message_text = \
             message_transfer_ampere(transfer_value=transfer_value)
    elif row.number_of_cyberlinks > 0:
        message_text = \
            message_transfer_with_links(
                transfer_value=round(transfer_value / 1e6, 1),
                links_amount=row.number_of_cyberlinks,
                address=row.address,
                token_for_links_amount=round(row.number_of_cyberlinks * gift_per_link / 1e6, 1),
                users_message=user_message)
    else:
        message_text = message_transfer_boot(int(transfer_value // 1e6), address=row.address)
    print(f'\nSend transfer message to user_id {row.user_id}, link number {row.number_of_cyberlinks}, cyber address {row.address}, '
          f'transfer value {transfer_value:>,} {"new bostrom address " + new_bostrom_address if new_bostrom_address else ""}')
    try:
        bot.send_message(
            chat_id=row.user_id,
            text=message_text,
            parse_mode='HTML',
            reply_markup=BASE_AFTER_SIGN_UP_KEYBOARD)
    except ApiTelegramException:
        print('Chat not found')


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


def compute_users_and_links(load_new_data: bool = LOAD_NEW_DATA) -> pd.DataFrame:
    if load_new_data:
        _users_and_links_df = get_users_and_links()
        with open("data/genesis_bostrom_testnet_5.json") as _jsonFile:
            _genesis_json = json.load(_jsonFile)
            _jsonFile.close()

        _genesis_balances_dict = {item['address']: [f"{int(coin['amount']):>,} {coin['denom']}"
                                                    for coin in item['coins']]
                                  for item in _genesis_json['app_state']['bank']['balances']}
        _users_and_links_df['bostrom_address'] = _users_and_links_df['address'].map(
            lambda x: address_to_address(x, 'bostrom'))
        _users_and_links_df['genesis'] = _users_and_links_df.bostrom_address.map(
            lambda x: _genesis_balances_dict[x] if x in _genesis_balances_dict.keys() else [])
        _users_and_links_df['genesis_str'] = _users_and_links_df.genesis.map(lambda x: ', '.join(x))
        _users_and_links_df.to_csv('users_and_links.csv')
    return pd.read_csv(
                'users_and_links.csv',
                index_col=0,
                dtype={'user_id': np.int64, 'account_name': str, 'number_of_cyberlinks': 'Int64'},
                converters={"genesis": lambda x: x.strip("[]").split(", ") if x != '[]' else []})


def transfer_tokens_handler(row: pd.Series, transfer_value: int, gift_per_link: float = 0, token_name: str = TOKEN_NAME) -> bool:
    _transfer_success, _transfer_error = \
        transfer_tokens(
            account_address=row.address,
            value=transfer_value,
            token_name=token_name)
    if _transfer_success:
        send_message_transfer(row=row, transfer_value=transfer_value, gift_per_link=gift_per_link, token_name=token_name)
        return True
    else:
        print(f'\nUnsuccessful transfer {transfer_value} {token_name} to {row.address}, user id {row.user_id}')
        return False


def run():
    if CREATE_NEW_ADDRESS_COLUMN:
        db_worker.rename_column(new_column_name='account_address_euler')
        db_worker.add_column()

    users_and_links_df = compute_users_and_links()
    total_cyberlinks = int(sum(users_and_links_df.number_of_cyberlinks))
    gift_per_link = round(TOTAL_GOL_GIFT/sum(users_and_links_df.number_of_cyberlinks))
    print(f'Total cyberLinks created by cyberdBot {total_cyberlinks:>,}\n'
          f'Gift per created cyberLink {gift_per_link:>,} {TOKEN_NAME}')

    for df_index in users_and_links_df.index:

        row = users_and_links_df.iloc[df_index].copy()
        token_amount = TRANSFER_VALUE_LEADERS if row.number_of_cyberlinks >= 10 else TRANSFER_VALUE_NEW_USERS
        transfer_value = token_amount + row.number_of_cyberlinks * gift_per_link

        if CREATE_NEW_ADDRESSES:
            row.address = sign_up_user(user_id=row.user_id, account_name=row.account_name)
            if row.address is None:
                continue
            db_worker.update_account_address(user_id=row.user_id, new_address=row.address)

        transfer_tokens_handler(row=row, transfer_value=transfer_value, gift_per_link=gift_per_link)
        transfer_tokens_handler(row=row, transfer_value=MILLIAMPERE_TRANSFER_VALUE, token_name=MILLIAMPERE_TOKEN_NAME)

        # send_message_genesis(row)

    print('Transferred Successfully!')


if __name__ == '__main__':
    run()
