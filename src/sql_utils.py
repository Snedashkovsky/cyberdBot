import sqlite3
from pandas import DataFrame


class SQLighter:
    """
    Class for working with SQLite DB
    Tables:
    - monikers
    - scheduler
    - accounts
    - cyberlinks
    """

    def __init__(self, database):
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def drop_table_monikers(self):
        """ Drop monikers table """
        with self.connection:
            return self.cursor.execute(
                '''DROP TABLE IF EXISTS monikers''').fetchall()

    def drop_table_scheduler(self):
        """ Drop scheduler state table """
        with self.connection:
            return self.cursor.execute(
                '''DROP TABLE IF EXISTS scheduler''').fetchall()

    def drop_table_accounts(self):
        """ Drop accounts table """
        with self.connection:
            return self.cursor.execute(
                '''DROP TABLE IF EXISTS accounts''').fetchall()

    def drop_table_cyberlinks(self):
        """ Drop accounts table """
        with self.connection:
            return self.cursor.execute(
                '''DROP TABLE IF EXISTS cyberlinks''').fetchall()

    def drop_all_tables(self):
        self.drop_table_monikers()
        self.drop_table_scheduler()
        self.drop_table_accounts()
        self.create_table_cyberlinks()

    def create_table_monikers(self):
        """ Create monikers table """
        with self.connection:
            return self.cursor.execute(
                '''CREATE TABLE IF NOT EXISTS monikers (
                       chat_id INTEGER NOT NULL,
                       moniker STRING NOT NULL,
                       ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''').fetchall()

    def create_table_scheduler(self):
        """ Create scheduler state table """
        with self.connection:
            return self.cursor.execute(
                '''CREATE TABLE IF NOT EXISTS scheduler (
                       chat_id INTEGER PRIMARY KEY NOT NULL,
                       state BOOL NOT NULL,
                       ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''').fetchall()

    def create_table_accounts(self):
        """ Create scheduler state table """
        with self.connection:
            return self.cursor.execute(
                '''CREATE TABLE IF NOT EXISTS accounts (
                       user_id INTEGER PRIMARY KEY NOT NULL,
                       account_name STRING NOT NULL,
                       account_address STRING NOT NULL,
                       ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''').fetchall()

    def create_table_cyberlinks(self):
        """ Create scheduler state table """
        with self.connection:
            return self.cursor.execute(
                '''CREATE TABLE IF NOT EXISTS cyberlinks (
                       cyberlink_hash STRING PRIMARY KEY NOT NULL, 
                       user_id INTEGER NOT NULL,
                       from_ipfs_hash STRING NOT NULL,
                       to_ipfs_hash STRING NOT NULL,
                       ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''').fetchall()

    def create_all_tables(self):
        self.create_table_monikers()
        self.create_table_scheduler()
        self.create_table_accounts()
        self.create_table_cyberlinks()

    def get_all_monikers(self):
        """ Get all chat ids and monikers lists """
        with self.connection:
            return self.cursor.execute(
                '''SELECT 
                       chat_id, 
                       group_concat(moniker) 
                   FROM  monikers 
                   GROUP BY chat_id''').fetchall()

    def get_moniker(self, chat_id: int):
        """ Get moniker list for chat_id """
        with self.connection:
            result = self.cursor.execute(
                f'''SELECT group_concat(moniker) 
                    FROM  monikers 
                    WHERE chat_id={chat_id}''').fetchall()[0][0]
            if result:
                return result.split(',')
            return []

    def get_all_scheduler_states(self):
        """ Get all chat ids and scheduler states """
        with self.connection:
            result = self.cursor.execute(
                f'''SELECT chat_id
                    FROM  scheduler
                    WHERE state = 1''').fetchall()
            print(result)
            if len(result) > 0:
                return [item[0] for item in result]
            return []

    def get_scheduler_state(self, chat_id: int):
        """ Get scheduler state for chat_id """
        with self.connection:
            result = self.cursor.execute(
                f'''SELECT state
                    FROM  scheduler 
                    WHERE chat_id={chat_id}''').fetchall()
            if result:
                return result[0][0]
            return 0

    def set_scheduler_state(self, chat_id: int, state: int):
        """ Set scheduler state for chat_id """
        with self.connection:
            if state == 1:
                return self.cursor.execute(
                    f"INSERT INTO scheduler (chat_id, state)  VALUES({chat_id}, '{state}')").fetchall()
            return self.cursor.execute(
                f"DELETE FROM scheduler WHERE chat_id={chat_id}").fetchall()

    def add_moniker(self, chat_id, moniker):
        """ Add moniker for chat_id """
        with self.connection:
            return self.cursor.execute(
                f"INSERT INTO monikers (chat_id, moniker)  VALUES({chat_id}, '{moniker}')").fetchall()

    def reset_moniker(self, chat_id: int):
        """ Reset moniker list for chat_id """
        with self.connection:
            result = self.cursor.execute(
                f'DELETE FROM monikers WHERE chat_id={chat_id}').fetchall()
            return len(result)

    def signup_user(self, user_id: int, account_name: str, account_address: str):
        """ Insert new user in the accounts table """
        # TODO Update `accounts` table and remove here `account_address_euler`
        with self.connection:
            return self.cursor.execute(
                f"""INSERT INTO accounts (user_id, account_name, account_address, account_address_euler) 
                    VALUES({user_id}, '{account_name}', '{account_address}', '')""").fetchall()

    def check_sign_user(self, user_id: int):
        """ Check if the user is signed up or not """
        with self.connection:
            if len(self.cursor.execute(f"SELECT * FROM accounts WHERE user_id={user_id}").fetchall()) > 0:
                return True
            return False

    def write_cyberlink(self, user_id: int, cyberlink_hash: str, from_ipfs_hash: str, to_ipfs_hash: str):
        """ Insert new cyberlink """
        with self.connection:
            self.cursor.execute(
                f"""INSERT INTO cyberlinks (user_id, cyberlink_hash, from_ipfs_hash, to_ipfs_hash) 
                    VALUES({user_id}, '{cyberlink_hash}', '{from_ipfs_hash}', '{to_ipfs_hash}')""").fetchall()

    def get_account_name(self, user_id: int):
        """ Get account address for user id """
        with self.connection:
            return self.cursor.execute(
                f"SELECT account_name FROM accounts WHERE user_id={user_id}").fetchall()[0][0]

    def get_account_address(self, user_id: int):
        """ Get account address for user id """
        with self.connection:
            return self.cursor.execute(
                f"SELECT account_address FROM accounts WHERE user_id={user_id}").fetchall()[0][0]

    def get_cyberlink_count(self, user_id: int):
        """ Get number of created cyberLinks for user id """
        with self.connection:
            return self.cursor.execute(
                f"SELECT count(*) FROM cyberlinks WHERE user_id={user_id}").fetchall()[0][0]

    def get_total_account_with_full_transfers(self):
        """ Get number of account with number of created cyberLinks more than 10 """
        with self.connection:
            return self.cursor.execute(
                """SELECT count(*) 
                   FROM (
                       SELECT 
                           user_id, 
                           count(*) as cyberlink_count 
                       FROM cyberlinks 
                       GROUP BY user_id 
                       HAVING cyberlink_count > 10)""").fetchall()[0][0]

    def get_df(self, query: str, columns=None):
        """ Get pandas dataframe from query result """
        with self.connection:
            return DataFrame(
                self.cursor.execute(query).fetchall(),
                columns=columns)

    def update_account_address(self, user_id: int, new_address: str):
        """ Update account address after moving to a new network or adding new address"""
        with self.connection:
            self.cursor.execute(
                f"""UPDATE accounts 
                    SET account_address = '{new_address}' 
                    WHERE user_id = {user_id}""").fetchall()

    def rename_column(self, new_column_name: str, old_column_name: str = 'account_address', table: str = 'accounts'):
        with self.connection:
            self.cursor.execute(
                f"""ALTER TABLE {table} RENAME COLUMN {old_column_name} TO {new_column_name}""").fetchall()

    def add_column(self, new_column_name: str = 'account_address', table: str = 'accounts'):
        with self.connection:
            self.cursor.execute(
                f"""ALTER TABLE {table} ADD COLUMN {new_column_name} STRING NOT NULL DEFAULT ''""").fetchall()

    def close(self):
        """ Close DB connection """
        self.connection.close()
