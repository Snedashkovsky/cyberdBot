from telebot.apihelper import ApiTelegramException
from src.bash_utils import transfer_eul_tokens
from config import BASE_AFTER_SIGN_UP_KEYBOARD, db_worker, bot

MESSAGE_TEXT_NEW_USER = '''
@cyberdBot additionally transferred <b>7.5 MEUL</b> to you.
If you create <b>10 links</b> with the bot, another <b>90 MEUL</b> will be transferred.
Remember, EUL tokens will not be migrated to the production network.
On the other hand, you can participate in the <b>Relevance</b> section of the <b>Game of Links</b> and get your share of the prize <b>500 GCYB ~ 230 ETH</b>.
Go for it!'''
MESSAGE_TEXT_LEADER = '''
@cyberdBot additionally transferred <b>90 MEUL</b> to you.
Remember, EUL tokens will not be migrated to the production network.
On the other hand, you can participate in the <b>Relevance</b> section of the <b>Game of Links</b> and get your share of the prize <b>500 GCYB ~ 230 ETH</b>.
Your bandwidth is enough to generate at least <b>100 links per day</b>.
Go for it!'''

TRANSFER_VALUE_NEW_USERS = 7_500_000
TRANSFER_VALUE_LEADERS = 90_000_000


def get_users_and_links():
    return db_worker.get_df(
        query='''
            SELECT
                acc.user_id,
                links.cyberlink_count,
                acc.account_address
            FROM (
                SELECT
                    user_id,
                    account_address
                FROM accounts
                ) as acc
            LEFT JOIN (
                SELECT
                    user_id,
                    count() as cyberlink_count
                FROM cyberlinks
                GROUP BY user_id
                ) as links
            ON links.user_id = acc.user_id''',
        columns=['user_id', 'number_of_cyberlinks', 'address']).fillna(0)


if __name__ == '__main__':

    users_and_links_df = get_users_and_links()

    for df_index in users_and_links_df.index:
        row = users_and_links_df.iloc[df_index].copy()
        if row.number_of_cyberlinks >= 10:
            message_text = MESSAGE_TEXT_LEADER
            transfer_value = TRANSFER_VALUE_LEADERS
        else:
            message_text = MESSAGE_TEXT_NEW_USER
            transfer_value = TRANSFER_VALUE_NEW_USERS
        print(row.user_id, row.number_of_cyberlinks, row.address, transfer_value)
        transfer_success, transfer_error = \
            transfer_eul_tokens(
                account_address=row.address,
                value=transfer_value)
        if transfer_success:
            try:
                bot.send_message(
                    chat_id=row.user_id,
                    text=message_text,
                    parse_mode='HTML',
                    reply_markup=BASE_AFTER_SIGN_UP_KEYBOARD)
            except ApiTelegramException:
                print('Chat not found')
        else:
            print(f'Unsuccessful transfer {transfer_value} EUL to {row.address}, user id {row.user_id}')
