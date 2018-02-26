import os

os.environ['ASYNC_TEST_TIMEOUT'] = os.environ.get('ASYNC_TEST_TIMEOUT', '15')


def setup_module():
    with open('build/test-environment') as env_file:
        for line in env_file:
            if line.startswith('export '):
                line = line[7:].strip()
            name, _, value = line.partition('=')
            if value.startswith(('"', "'")):
                if value.endswith(value[0]):
                    value = value[1:-1]
            os.environ[name] = value
