from subprocess import Popen, PIPE
import logging
import re

from config import CYBERLINK_CREATION_QUERY, ACCOUNT_CREATION_QUERY, TRANSFER_QUERY, \
                   UNJAIL_VALIDATOR_QUERY, DELEGATE_QUERY, INVESTMINT_QUERY, VALIDATOR_ADDRESS, TOKEN_NAME


def execute_bash(bash_command: str):
    if len(bash_command.split('"')) == 1:
        bash_command_list = bash_command.split()
    elif len(bash_command.split('"')) == 2:
        bash_command_list = \
            bash_command.split('"')[0].split() + \
            [bash_command.split('"')[1]]
    elif len(bash_command.split('"')) > 2:
        bash_command_list = \
            bash_command.split('"')[0].split() + \
            [bash_command.split('"')[1]] + \
            [item for items in bash_command.split('"')[2:] for item in items.split()]
    else:
        return None, f'Cannot split bash command {bash_command}'
    popen_process = Popen(bash_command_list, stdout=PIPE)
    return popen_process.communicate(timeout=15)


def extract_from_console(console_output, keys: list):
    console_output_split = \
        [item.replace(' ', '').replace('"', '').split(':')
         for item in re.split('{|}|,|\*|\\\\n|\\\\r',str(console_output))]
    return [[item[0], item[1].split('\\')[0]] for item in console_output_split if item[0] in keys]


def create_cyberlink(account_name: str, from_hash: str, to_hash: str, query: str = CYBERLINK_CREATION_QUERY):
    try:
        output, error_execute_bash = execute_bash(f'{query} {account_name} {from_hash} {to_hash}')
        if error_execute_bash:
            logging.error(
                f"cyberLink was not created. Account {account_name}, from {from_hash}, to {to_hash}. "
                f"Error {error_execute_bash}")
            return None, error_execute_bash
        raw_log = extract_from_console(output, ['rawlog'])[0][1]
        if raw_log == 'not enough personal bandwidth'.replace(' ', ''):
            logging.info(
                f"cyberLink was not created. Account {account_name}, from {from_hash}, to {to_hash}. Not enough "
                f"personal bandwidth")
            return None, 'not enough personal bandwidth'
        tx_hash = extract_from_console(output, ['txhash'])[0][1]
        logging.info(
            f"cyberLink was created. Account {account_name}, from {from_hash}, to {to_hash}. tx {tx_hash}")
        return tx_hash, None
    except Exception as error_parsing:
        logging.error(
            f"cyberLink was not created. Account {account_name}, from {from_hash}, to {to_hash}. Error {error_parsing}")
        return None, error_parsing


def create_account(account_name: str, query: str = ACCOUNT_CREATION_QUERY):
    try:
        output, error_execute_bash = \
            execute_bash(f'{query} {account_name}')
        if 'override the existing name' in str(output):
            return None, 'This account already exists'
        if output:
            account_address = extract_from_console(output, ['address'])[0][1]
            if len(str(output).split('\\n')[-3]) > 40:
                account_mnemonic_phrase = str(output).split('\\n')[-3].split('\\')[0]
            elif len(str(output).split('\\n')[-2]) > 40:
                account_mnemonic_phrase = str(output).split('\\n')[-2].split('\\')[0]
            elif len(str(output).split('\\n')[-1]) > 40:
                account_mnemonic_phrase = str(output).split('\\n')[-1].split('\\')[0]
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


def transfer_tokens(account_address: str, value: int, query: str = TRANSFER_QUERY):
    try:
        output, error_execute_bash = \
            execute_bash(f'{query} {account_address} {str(value)+TOKEN_NAME.lower()}')
        if len(extract_from_console(output, ['txhash'])) > 0:
            logging.info(
                f"Tokens was transferred to {account_address} value {value}{TOKEN_NAME} "
                f"txhash {extract_from_console(output, ['txhash'])}")
            return True, None
        logging.error(
            f"Tokens was not transferred to {account_address} value {value}{TOKEN_NAME}. Error {error_execute_bash}")
        return None, error_execute_bash
    except Exception as error_transfer_tokens:
        logging.error(
            f"Tokens was not transferred to {account_address} value {value}{TOKEN_NAME}. Error {error_transfer_tokens}")
        return None, error_transfer_tokens


def delegate_tokens(account_address: str, value: int, validator: str = VALIDATOR_ADDRESS, query: str = DELEGATE_QUERY):
    try:
        output, error_execute_bash = \
            execute_bash(f'{query} {account_address} {str(value)+TOKEN_NAME.lower()} {validator}')
        if len(extract_from_console(output, ['txhash'])) > 0 or len(extract_from_console(output, ['txhash'])) > 0:
            logging.info(
                f"Tokens was delegated from {account_address} value {value}{TOKEN_NAME} "
                f"txhash {extract_from_console(output, ['txhash'])}")
            return True, None
        logging.error(
            f"Tokens was not delegated from {account_address} value {value}{TOKEN_NAME}. Error {error_execute_bash}")
        return None, error_execute_bash
    except Exception as error_transfer_tokens:
        logging.error(
            f"Tokens was not delegated from {account_address} value {value}{TOKEN_NAME}. Error {error_transfer_tokens}")
        return None, error_transfer_tokens


def investmint_tokens(account_address: str, value: int, investmint_token: str = 'amper', query: str = INVESTMINT_QUERY):
    try:
        output, error_execute_bash = \
            execute_bash(f'{query} {account_address} {str(value)+"s"+TOKEN_NAME.lower()} {investmint_token}')
        if len(extract_from_console(output, ['txhash'])) > 0:
            logging.info(
                f"Tokens was investminted from {account_address} to {investmint_token} value {value}s{TOKEN_NAME} "
                f"txhash {extract_from_console(output, ['txhash'])}")
            return True, None
        logging.error(
            f"Tokens was not investminted from {account_address} to {investmint_token} value {value}s{TOKEN_NAME}. "
            f"Error {error_execute_bash}")
        return None, error_execute_bash
    except Exception as error_transfer_tokens:
        logging.error(
            f"Tokens was not investminted from {account_address} to {investmint_token} value {value}s{TOKEN_NAME}. "
            f"Error {error_transfer_tokens}")
        return None, error_transfer_tokens


def unjail_validator(query: str = UNJAIL_VALIDATOR_QUERY):
    try:
        output, error_execute_bash = \
            execute_bash(f'{query}')
        if len(extract_from_console(output, ['txhash'])) > 0:
            logging.info(
                f"Unjail transaction was completed successfully"
                f"txhash {extract_from_console(output, ['txhash'])}")
            return True, None
        logging.error(
            f"Unjail transaction was not completed successfully. Error {error_execute_bash}")
        return None, error_execute_bash
    except Exception as error_transfer_tokens:
        logging.error(
            f"Unjail transaction was not completed successfully. Error {error_transfer_tokens}")
        return None, error_transfer_tokens
