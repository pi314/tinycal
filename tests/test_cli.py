import unittest

try:
    from io import StringIO
    from unittest.mock import patch
except:
    from StringIO import StringIO
    from mock import patch


def setUpModule():
    import datetime
    import sys

    # fix search path since executing `pytest`
    # though it can be fixed by make `tests` folder to be Python package, this way
    # is more straightforward
    sys.path.insert(0, '')
    from tinycal import config
    sys.path.pop(0)

    # set today is 2018.10.13 the day of generating test data
    config.today = datetime.date(2018, 10, 13)


class ArgumentsTest(unittest.TestCase):
    @patch('sys.stdout', new_callable=StringIO)
    def run_cmd(self, args, buff):
        import sys
        from tinycal import tcal
        sys.argv = [''] + args
        tcal.main()
        return buff.getvalue()

    def assert_command_output(self, args, expected):
        output = self.run_cmd(args)
        if output != expected:
            for line in output.splitlines(): print(repr(line))
            for line in expected.splitlines(): print(repr(line))
            raise AssertionError


def generate_case(args):
    file_name = args
    file_path = 'tests/testdata/%s' % file_name
    case_name = 'test_%s' % file_name
    command = 'python -m tinycal %s' % args
    #print(f'{command} > {file_name}')  # list commands to generate test data

    with open(file_path) as f:
        expected = f.read()

    def case(self):
        self.assert_command_output(args.split(), expected)

    return case_name, case


for args in [
        '2018 10',
        '-3 2018 10',
        '-3 --col 2 2018 10',
        '-3 --col 2 -w 2018 10',
        '-3 --col 2 -S 2018 10',
        '-3 --col 2 -nb 2018 10',
        '-3 --col 2 -nb -S 2018 10',
        '-A 3 -B 2 --col 3',
        '-A 3 -B 2 --col 4',
        '-A 1 -B 1 --col 4',
        ]:
    case_name, case = generate_case(args)
    setattr(ArgumentsTest, case_name, case)
