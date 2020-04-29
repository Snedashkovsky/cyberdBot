from subprocess import Popen, PIPE

from config import VALIDATOR_QUERY


def validators_state(shell_query=VALIDATOR_QUERY):
    def execute_bash(bash_command):
        process = Popen(bash_command.split(), stdout=PIPE)
        return process.communicate()

    output, _ = execute_bash(shell_query)

    validator_data_list = [item.replace(' ', '').split(':') for item in str(output).split('\\n')]
    validator_data_list = [item for item in validator_data_list if item[0] in ('jailed', 'moniker')]
    keys = [item[1] for item in validator_data_list[1::2]]
    values = [item[1] for item in validator_data_list[::2]]
    values = list(map(lambda x: 'unjailed' if x == 'false' else 'jailed', values))
    return dict(zip(keys, values))
