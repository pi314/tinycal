import unittest


ARGS_LIST = [
        '2018 10',
        '-3 2018 10',
        '-3 --col 2 2018 10',
        '-3 --col 2 -w 2018 10',
        '-3 --col 2 -S 2018 10',
        '-3 --col 2 -nb 2018 10',
        '-3 --col 2 -nb -S 2018 10',
        ]


def generate_case(args):
    file_name = args.replace('-', '_').replace(' _', '_').replace(' ', '_')
    file_path = 'tests/testdata/%s' % file_name
    case_name = 'test_%s' % file_name
    command = 'python -m tinycal %s' % args
    #print(f'{command} > {file_name}')  # list commands to generate test data

    with open(file_path) as f:
        expected = f.read()

    def case(self):
        self.assertCommand(command, expected)

    return case_name, case


class ArgumentsTest(unittest.TestCase):
    def run_cmd(self, cmd):
        import subprocess
        output = subprocess.check_output(cmd, shell=True)
        return output.decode()

    def assertCommand(self, cmd, expected):
        output = self.run_cmd(cmd)
        if output != expected:
            from pprint import pprint
            pprint(list(map(repr, output.splitlines())))
            pprint(list(map(repr, expected.splitlines())))
            raise AssertionError


for args in ARGS_LIST:
    case_name, case = generate_case(args)
    setattr(ArgumentsTest, case_name, case)
