from subprocess import Popen, PIPE

from config import VALIDATOR_QUERY, CYBERLINK_CREATION_QUERY


def execute_bash(bash_command):
    process = Popen(bash_command.split(), stdout=PIPE)
    return process.communicate()


def validators_state(shell_query=VALIDATOR_QUERY):
    try:
        output, error_execute_bash = execute_bash(shell_query)
        if error_execute_bash:
            print(error_execute_bash)
            return None, error_execute_bash
        validator_data_list = [item.replace(' ', '').split(':') for item in str(output).split('\\n')]
        validator_data_list = [item for item in validator_data_list if item[0] in ('jailed', 'moniker')]
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


def create_cyberlink(from_hash, to_hash, query=CYBERLINK_CREATION_QUERY):
    try:
        output, error_execute_bash = execute_bash(f'{query} {from_hash} {to_hash}')
        if error_execute_bash:
            print(error_execute_bash)
            return None, error_execute_bash
        output = [item.replace(' ', '').split(':') for item in str(output).split('\\n')]
        tx_hash = [item[1] for item in output if item[0] == 'txhash'][0]
        tx_hash = tx_hash.split('\\')[0]
        return tx_hash, None
    except Exception as error_parsing:
        print(error_parsing)
        return None, error_parsing


def test_create_cyberlink():
    tx_hash, _ = create_cyberlink('', '', query='cat ./tests/create_cyberlink_test')
    assert tx_hash == 'C97489299E9FE23FDE5F85AF85C076D869648577A9EE914E5A0332A6C515DE46'


def create_account(account):
    pass
