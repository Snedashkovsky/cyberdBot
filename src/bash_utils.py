from subprocess import Popen, PIPE

from config import VALIDATOR_QUERY, CYBERLINK_CREATION_QUERY, ACCOUNT_CREATION_QUERY, TRANSFER_EUL_QUERY


def execute_bash(bash_command):
    process = Popen(bash_command.split(), stdout=PIPE)
    return process.communicate()


def extract_from_console(console_output, keys):
    console_output = [item.replace(' ', '').split(':') for item in str(console_output).split('\\n')]
    return [[item[0], item[1].split('\\')[0]] for item in console_output if item[0] in keys]


def validators_state(shell_query=VALIDATOR_QUERY):
    try:
        output, error_execute_bash = execute_bash(shell_query)
        if error_execute_bash:
            print(error_execute_bash)
            return None, error_execute_bash
        validator_data_list = extract_from_console(output, ['jailed', 'moniker'])
        keys = [item[1] for item in validator_data_list[1::2]]
        values = [item[1] for item in validator_data_list[::2]]
        values = list(map(lambda x: 'unjailed' if x == 'false' else 'jailed', values))
        return dict(zip(keys, values)), None
    except Exception as error_parsing:
        print(error_parsing)
        return None, error_parsing


def test_validators_state():
    validator_list, _ = validators_state(shell_query='cat ./tests/validators_query_test')
    assert validator_list == \
           {'blue_blue': 'unjailed',
            'papsan': 'jailed',
            'dobry': 'unjailed',
            'litvintech': 'unjailed',
            'redbull': 'jailed',
            'Developer': 'unjailed',
            'sta': 'jailed',
            'stardust': 'unjailed',
            'cyberG': 'unjailed',
            'eto_piter_detka': 'unjailed',
            'ParadigmCitadel': 'unjailed',
            'groovybear': 'unjailed',
            'space': 'unjailed'}


def create_cyberlink(account_name, from_hash, to_hash, query=CYBERLINK_CREATION_QUERY):
    try:
        output, error_execute_bash = execute_bash(f'{query} {account_name} {from_hash} {to_hash}')
        if error_execute_bash:
            print(error_execute_bash)
            return None, error_execute_bash
        rawlog = extract_from_console(output, ['rawlog'])[0][1]
        if rawlog == 'not enough personal bandwidth'.replace(' ', ''):
            return None, 'not enough personal bandwidth'
        tx_hash = extract_from_console(output, ['txhash'])[0][1]
        return tx_hash, None
    except Exception as error_parsing:
        print(error_parsing)
        return None, error_parsing


def test_create_cyberlink():
    tx_hash, _ = create_cyberlink('', '', query='cat ./tests/create_cyberlink_test')
    assert tx_hash == 'C97489299E9FE23FDE5F85AF85C076D869648577A9EE914E5A0332A6C515DE46'


def create_account(account_name, query=ACCOUNT_CREATION_QUERY):
    try:
        output, error_execute_bash = \
            execute_bash(f'{query} {account_name}')
        if 'override the existing name' in str(output):
            return None, 'this account already exists'
        if output:
            account_address = extract_from_console(output, ['address'])[0][1]
            account_mnemonic_phrase = str(output).split('\\n')[-2].split('\\')[0]
            if account_address:
                account_data = {'name': account_name,
                                'address': account_address,
                                'mnemonic_phrase': account_mnemonic_phrase}
                return account_data, None
        return None, error_execute_bash
    except Exception as error_account_creation:
        print(error_account_creation)
        return None, error_account_creation


def transfer_eul_tokens(account_address, value=2_500_000, query=TRANSFER_EUL_QUERY):
    try:
        output, error_execute_bash = \
            execute_bash(f'{query} {account_address} {str(value)+"eul"}')
        if len(extract_from_console(output, ['txhash'])) > 0:
            return True, None
        return None, error_execute_bash
    except Exception as error_account_creation:
        print(error_account_creation)
        return None, error_account_creation
