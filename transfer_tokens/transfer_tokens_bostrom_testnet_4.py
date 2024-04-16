import json
import pandas as pd
from cyberpy import address_to_address
from telebot.apihelper import ApiTelegramException

from src.bash_utils import transfer_tokens, create_account
from config import BASE_AFTER_SIGN_UP_KEYBOARD, db_worker, bot, TOKEN_NAME, CYBERPAGE_URL, CYBER_CHAIN_ID


TRANSFER_VALUE_NEW_USERS = 10_000_000
TRANSFER_VALUE_LEADERS = 100_000_000
TOTAL_GOL_GIFT = 1_178_234_463
LOAD_NEW_DATA = True
CREATE_NEW_ADDRESS_COLUMN = False
NEW_USER_MESSAGE = f'If you create <b>10 links</b> with the bot, another <b>90 M{TOKEN_NAME}</b> will be transferred.'


def message_genesis(cyber_address: str, bostrom_address: str, genesis_balance: str) -> str:
    return f'''
Also your bostrom address <b>{bostrom_address}</b> was included in the {CYBER_CHAIN_ID} Genesis.
Your genesis balance is <b>{genesis_balance}</b>.
{CYBERPAGE_URL}/contract/{bostrom_address}/wallet
@cyberdBot sent the mnemonic phrase for the cyber address <b>{cyber_address}</b> during sign up.
You can use this mnemonic phrase to access the bostrom address by any wallet (e.g. Keplr).'''


def message_transfer(transfer_value) -> str:
    return f'''
@cyberdBot transferred <b>{transfer_value} M{TOKEN_NAME}</b> to you.
Remember, {TOKEN_NAME} tokens will not be migrated to the production network.
Let's delegate, investmint to Volt and Amper by https://rebyc.cyber.page/mint
Your bandwidth can be enough to generate at least <b>7 links per day</b> after investminting in Amper.
{NEW_USER_MESSAGE}
Go for it!'''


def message_transfer_with_links(transfer_value, links_amount, token_for_links_amount, users_message) -> str:
    return f'''
@cyberdBot received 1,178 M{TOKEN_NAME} from Game of Link and distributes this prize between accounts in proportion to the number of created cyberLinks. You created {int(links_amount):>,} cyberLinks.
<b>{transfer_value} M{TOKEN_NAME}</b> has been transferred to you, including <b>{token_for_links_amount} M{TOKEN_NAME}</b> reward for cyberLink creation.
Remember, {TOKEN_NAME} tokens will not be migrated to the production network.
Let's delegate, investmint to Volt and Amper by https://rebyc.cyber.page/mint and Keplr wallet.
Your bandwidth can be enough to generate at least <b>7 links per day</b> after investminting in Amper.
{users_message}
Go for it!'''


def sign_up_user(user_id, account_name):
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
        print(
            user_id,
            f'Account not created. Error: {create_account_error}')
    return


def send_message_genesis(row):
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


def send_message_transfer(row, transfer_value, new_bostrom_address):
    user_message = '' if row.number_of_cyberlinks >= 10 else NEW_USER_MESSAGE
    if row.number_of_cyberlinks > 0:
        message_text = \
            message_transfer_with_links(
                round(transfer_value/ 1e6, 1),
                row.number_of_cyberlinks,
                round(row.number_of_cyberlinks * gift_per_link / 1e6, 1),
                user_message)
    else:
        message_text = message_transfer(transfer_value // 1e6)
    print(f'\nSend transfer message to {row.user_id} link number {row.number_of_cyberlinks} cyber address {row.address} '
          f'transfer value {transfer_value} new bostrom address {new_bostrom_address}')
    try:
        bot.send_message(
            chat_id=row.user_id,
            text=message_text,
            parse_mode='HTML',
            reply_markup=BASE_AFTER_SIGN_UP_KEYBOARD)
    except ApiTelegramException:
        print('Chat not found')


def get_users_and_links():
    return db_worker.get_df(
        query='''
            SELECT
                acc.user_id,
                acc.account_name,
                links.cyberlink_count,
                acc.account_address_euler
            FROM (
                SELECT
                    user_id,
                    account_name,
                    account_address_euler
                FROM accounts
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


def compute_users_and_links(load_new_data: bool = LOAD_NEW_DATA):
    if load_new_data:
        _users_and_links_df = get_users_and_links()

        with open("../data/genesis_bostrom_testnet_4.json") as _jsonFile:
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
    return pd.read_csv('users_and_links.csv')


if __name__ == '__main__':

    if CREATE_NEW_ADDRESS_COLUMN:
        db_worker.rename_column(new_column_name='account_address_euler')
        db_worker.add_column()

    users_and_links_df = compute_users_and_links()
    total_cyberlinks = int(sum(users_and_links_df.number_of_cyberlinks))
    gift_per_link = round(TOTAL_GOL_GIFT/sum(users_and_links_df.number_of_cyberlinks))
    print(f'Total cyberLinks created by cyberdBot {total_cyberlinks:>,}\n'
          f'Gift per created cyberLink {gift_per_link:>,} {TOKEN_NAME}')

    for df_index in users_and_links_df.index[7:8]:
        row = users_and_links_df.iloc[df_index].copy()
        new_bostrom_address = sign_up_user(user_id=row.user_id, account_name=row.account_name)
        if new_bostrom_address is None:
            continue
        token_amount = TRANSFER_VALUE_LEADERS if row.number_of_cyberlinks >= 10 else TRANSFER_VALUE_NEW_USERS
        transfer_value = token_amount + row.number_of_cyberlinks * gift_per_link
        transfer_success, transfer_error = \
            transfer_tokens(
                account_address=new_bostrom_address,
                value=transfer_value)
        if transfer_success:
            send_message_transfer(row, transfer_value, new_bostrom_address)
            db_worker.update_account_address(user_id=row.user_id, new_address=new_bostrom_address)
        else:
            print(f'\nUnsuccessful transfer {transfer_value} {TOKEN_NAME} to {row.address}, user id {row.user_id}')

        send_message_genesis(row)

    print('Transferred Successfully!')
