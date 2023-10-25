import re

from cyberutils.bash import execute_bash

from config import CYBERLINK_CREATION_QUERY, ACCOUNT_CREATION_QUERY, TRANSFER_QUERY, IPFS_RESTART_QUERY, \
    TOKEN_NAME, logging


def extract_from_console(console_output: bytes, keys: list) -> list:
    _console_output_split = \
        [item.replace(' ', '').replace('"', '').split(':')
         for item in re.split('{|}|,|\*|\\\\n|\\\\r', str(console_output))]
    return [[item[0], item[1].split('\\')[0]] for item in _console_output_split if item[0] in keys]


def create_cyberlink(account_name: str, from_hash: str, to_hash: str, query: str = CYBERLINK_CREATION_QUERY):
    if from_hash == to_hash:
        logging.error(
            f"cyberLink was not created. Account {account_name}, from {from_hash}, to {to_hash}. "
            f"Error self cyberlink")
        return None, 'From and To CID is equal. Cannot create cyberLink to self beginning'
    try:
        _output, error_execute_bash = execute_bash(f'{query} {account_name} {from_hash} {to_hash}')

        if error_execute_bash:
            logging.error(
                f"cyberLink was not created. Account {account_name}, from {from_hash}, to {to_hash}. "
                f"Error {error_execute_bash}")
            return None, 'Cannot connect to node'

        _logs = extract_from_console(_output, ['logs'])[0][1]
        _raw_log = extract_from_console(_output, ['raw_log'])[0][1]
        _creation_error = extract_from_console(_output, ['Error'])

        if (len(_raw_log) > 0 and _raw_log[0][1] == 'not enough personal bandwidth'.replace(' ', '')) \
                or (len(_creation_error) > 0):
            logging.info(
                f"cyberLink was not created. Account {account_name}, from {from_hash}, to {to_hash}. Not enough "
                f"personal bandwidth. Error {_creation_error}")
            return None, 'not enough personal bandwidth'

        elif len(_raw_log) > 0 and _raw_log[0][-1].find(
                'failed to execute message; message index'.replace(' ', '')) != -1:
            logging.info(
                f"cyberLink already exists. Account {account_name}, from {from_hash}, to {to_hash}. "
                f"Error {_creation_error}")

        tx_hash = extract_from_console(_output, ['txhash'])[0][1]
        logging.info(
            f"cyberLink was created. Account {account_name}, from {from_hash}, to {to_hash}. tx {tx_hash}")
        return tx_hash, None

    except Exception as error_parsing:
        logging.error(
            f"cyberLink was not created. Account {account_name}, from {from_hash}, to {to_hash}. Error {error_parsing}")
        return None, error_parsing


def create_account(account_name: str, query: str = ACCOUNT_CREATION_QUERY):
    try:
        _output, error_execute_bash = \
            execute_bash(f'{query} {account_name}')
        if 'override the existing name' in str(_output):
            return None, 'This account already exists'
        if _output:
            account_address = extract_from_console(_output, ['address'])[0][1]
            if len(str(_output).split('\\n')[-3]) > 40:
                account_mnemonic_phrase = str(_output).split('\\n')[-3].split('\\')[0]
            elif len(str(_output).split('\\n')[-2]) > 40:
                account_mnemonic_phrase = str(_output).split('\\n')[-2].split('\\')[0]
            elif len(str(_output).split('\\n')[-1]) > 40:
                account_mnemonic_phrase = str(_output).split('\\n')[-1].split('\\')[0]
            else:
                return None, 'Cannot get mnemonic phrase'
            if account_address:
                account_data = {'name': account_name,
                                'address': account_address,
                                'mnemonic_phrase': account_mnemonic_phrase}
                logging.info(
                    f"Account {account_name} was created. Account address {account_address}")
                return account_data, None
        logging.error(
            f"Account {account_name} was not created. Error {error_execute_bash}")
        return None, error_execute_bash
    except Exception as error_account_creation:
        logging.error(
            f"Account {account_name} was not created. Error {error_account_creation}")
        return None, error_account_creation


def transfer_tokens(account_address: str, value: int, token_name: str = TOKEN_NAME, query: str = TRANSFER_QUERY):
    try:
        _output, error_execute_bash = \
            execute_bash(f'{query} {account_address} {str(value) + token_name.lower()}')
        if len(extract_from_console(_output, ['txhash'])[0][1]) > 0:
            logging.info(
                f"Tokens was transferred to {account_address} value {value}{token_name} "
                f"txhash {extract_from_console(_output, ['txhash'])}")
            return True, None
        logging.error(
            f"Tokens was not transferred to {account_address} value {value}{token_name}. Error {error_execute_bash}")
        return None, error_execute_bash
    except Exception as error_transfer_tokens:
        logging.error(
            f"Tokens was not transferred to {account_address} value {value}{token_name}. Error {error_transfer_tokens}")
        return None, error_transfer_tokens


def restart_ipfs_node(query: str = IPFS_RESTART_QUERY):
    try:
        output, error_execute_bash = \
            execute_bash(query)
        if error_execute_bash:
            logging.error(
                f"IPFS node restart was not completed successfully. Error {error_execute_bash}")
            return None, error_execute_bash
        logging.info(
            f"IPFS node restart was completed successfully")
        return True, None
    except Exception as error_ipfs_restart:
        logging.error(
            f"IPFS node restart was not completed successfully. Error {error_ipfs_restart}")
        return None, error_ipfs_restart
