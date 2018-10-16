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


def assert_command_output(output, expected):
    if output != expected:
        for line in output.splitlines(): print(line.__repr__())
        for line in expected.splitlines(): print(line.__repr__())
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
        output = self.run_cmd(args.split())
        assert_command_output(output, expected)

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


class ConfigTest(unittest.TestCase):
    config_path = '/tmp/calrc'

    def setUp(self):
        import os.path
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

        import tinycal.tcal
        tinycal.tcal.CALRC += (self.config_path,)

    def tearDown(self):
        import tinycal
        tinycal.CALRC = tinycal.CALRC[:-1]

        import os
        import os.path
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    @patch('sys.stdout', new_callable=StringIO)
    def test_color_config(self, buff):
        expected_path = 'tests/testdata/color_config'

        import os.path
        assert os.path.exists(expected_path)

        with open(self.config_path, 'w') as f:
            f.write(
                "title.color = black:cyan\n"
                "wk.color = black:white\n"
                "today.color = RED\n"
                "weekday.color = YELLOW\n"
                "weekday.sunday.color = GREEN\n"
                "weekday.saturday.color = GREEN\n"
                )

        import sys
        sys.argv = ['', '-3']

        import tinycal.tcal
        tinycal.tcal.main()

        output = buff.getvalue()
        with open(expected_path) as f:
            expected = f.read()

        assert_command_output(output, expected)
