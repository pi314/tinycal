import unittest

import datetime

from io import StringIO
from unittest.mock import patch, mock_open
from os.path import join


from tinycal import tcal



class TinyCalTestCase(unittest.TestCase):
    @property
    def calrc(self):
        return StringIO('')

    @property
    def args(self):
        return []

    @patch('sys.stdout', new_callable=StringIO)
    def run_with_args(self, args, stdout):
        tcal.CALRCS = [self.calrc]
        tcal.main(self.args + args)
        return stdout

    def check_output(self, answer_file, stdout):
        with open(join('tests', 'expected_output', answer_file)) as f:
            for a, b in zip(stdout.getvalue().split('\n'), f.read().split('\n')):
                self.assertEqual(a, b)


class NoBorderLayoutTestcase(TinyCalTestCase):
    @property
    def calrc(self):
        return StringIO('')

    @property
    def args(self):
        return ['--border=off', '--color=never', '--today=2020/03/14', '--wk', '--fill']

    def test_nofill_nowk(self):
        stdout = self.run_with_args(['--no-wk', '--no-fill'])
        self.check_output('border=off nofill nowk', stdout)

    def test_1_month(self):
        stdout = self.run_with_args([])
        self.check_output('border=off', stdout)

    def test_3_months(self):
        stdout = self.run_with_args(['-3'])
        self.check_output('border=off 3months', stdout)

    def test_whole_year(self):
        stdout = self.run_with_args(['2020'])
        self.check_output('border=off 2020', stdout)


class AsciiBorderLayoutTestcase(TinyCalTestCase):
    def setUp(self):
        self.border = 'ascii,full'

    @property
    def calrc(self):
        return StringIO('')

    @property
    def args(self):
        return ['--border=' + self.border, '--color=never', '--today=2020/03/14', '--fill', '--wk']

    def test_layout_nofill_nowk(self):
        stdout = self.run_with_args(['--no-wk', '--no-fill'])
        self.check_output('border=ascii nofill nowk', stdout)

    def test_layout_basic(self):
        self.border = 'ascii,basic'
        stdout = self.run_with_args([])
        self.check_output('border=ascii,basic', stdout)

    def test_1_month(self):
        stdout = self.run_with_args([])
        self.check_output('border=ascii', stdout)

    def test_3_months(self):
        stdout = self.run_with_args(['-3'])
        self.check_output('border=ascii 3months', stdout)

    def test_whole_year(self):
        stdout = self.run_with_args(['2020'])
        self.check_output('border=ascii 2020', stdout)


class SingleBorderLayoutTestcase(TinyCalTestCase):
    def setUp(self):
        self.border = 'single,full'

    @property
    def calrc(self):
        return StringIO('')

    @property
    def args(self):
        return ['--border=' + self.border, '--color=never', '--today=2020/03/14', '--fill', '--wk']

    def test_layout_nofill_nowk(self):
        stdout = self.run_with_args(['--no-wk', '--no-fill'])
        self.check_output('border=single nofill nowk', stdout)

    def test_layout_basic(self):
        self.border = 'single,basic'
        stdout = self.run_with_args([])
        self.check_output('border=single,basic', stdout)

    def test_1_month(self):
        stdout = self.run_with_args([])
        self.check_output('border=single', stdout)

    def test_3_months(self):
        stdout = self.run_with_args(['-3'])
        self.check_output('border=single 3months', stdout)

    def test_whole_year(self):
        stdout = self.run_with_args(['2020'])
        self.check_output('border=single 2020', stdout)


class DoubleBorderLayoutTestcase(TinyCalTestCase):
    def setUp(self):
        self.border = 'double,full'

    @property
    def calrc(self):
        return StringIO('')

    @property
    def args(self):
        return ['--border=' + self.border, '--color=never', '--today=2020/03/14', '--fill', '--wk']

    def test_layout_nofill_nowk(self):
        stdout = self.run_with_args(['--no-wk', '--no-fill'])
        self.check_output('border=double nofill nowk', stdout)

    def test_layout_basic(self):
        self.border = 'double,basic'
        stdout = self.run_with_args([])
        self.check_output('border=double,basic', stdout)

    def test_1_month(self):
        stdout = self.run_with_args([])
        self.check_output('border=double', stdout)

    def test_3_months(self):
        stdout = self.run_with_args(['-3'])
        self.check_output('border=double 3months', stdout)

    def test_whole_year(self):
        stdout = self.run_with_args(['2020'])
        self.check_output('border=double 2020', stdout)


class ContiguousModeTestcase(TinyCalTestCase):
    @property
    def calrc(self):
        return StringIO('')

    @property
    def args(self):
        return ['--border=single', '--color=never', '--today=2020/03/14', '--fill', '--wk', '--cont']

    def test_1_month(self):
        stdout = self.run_with_args([])
        self.check_output('border=single', stdout)

    def test_3_months_nofill_nowk(self):
        stdout = self.run_with_args(['-3', '--no-fill', '--no-wk'])
        self.check_output('cont 3months nofill nowk', stdout)

    def test_3_months(self):
        stdout = self.run_with_args(['-3'])
        self.check_output('cont 3months', stdout)


class WeldTestcase(TinyCalTestCase):
    @property
    def calrc(self):
        return StringIO('')

    @property
    def args(self):
        return ['--border=single,noweld', '--color=never', '--today=2020/03/14', '--fill', '--wk']

    def test_noweld(self):
        stdout = self.run_with_args(['2020'])
        self.check_output('noweld', stdout)


class LangTestcase(TinyCalTestCase):
    @property
    def calrc(self):
        return StringIO('')

    @property
    def args(self):
        return ['--border=single', '--color=never', '--today=2020/03/14', '--fill', '--wk']

    def test_en(self):
        stdout = self.run_with_args(['--lang=en', '2020'])
        self.check_output('border=single 2020', stdout)

    def test_zh(self):
        stdout = self.run_with_args(['--lang=zh', '2020'])
        self.check_output('lang=zh', stdout)

    def test_jp(self):
        stdout = self.run_with_args(['--lang=jp', '2020'])
        self.check_output('lang=jp', stdout)

    def test_jp_cont(self):
        stdout = self.run_with_args(['--lang=jp', '--cont', '2020'])
        self.check_output('lang=jp cont', stdout)


class ColorTestcase(TinyCalTestCase):
    @property
    def calrc(self):
        return StringIO('''
title.color = black:cyan
wk.color = black:white
today.color = black:white
weekday.color = YELLOW
weekday.sunday.color = GREEN
weekday.saturday.color = GREEN
sunday.color = RED
saturday.color = RED
border.color = magenta
today.wk.color = white
marks = MOCK_MARKS
                ''')

    @property
    def args(self):
        return ['--border=single,full', '--color=always', '--today=2020/03/14', '--fill', '--wk']

    def test_color(self):
        def precise_mock_open(fname, *args, **kwargs):
            if fname == 'MOCK_MARKS':
                return StringIO('''
2020/03/18 BLUE # comment
2020/03/19
2020/03/20 invalid:color
''')

            else:
                return open(*args, **kwargs)

        def precise_mock_exists(path):
            if fname == 'MOCK_MARKS':
                return True

            return False

        with patch('builtins.open', new=precise_mock_open) as mock_file:
            stdout = self.run_with_args([])

        self.check_output('color', stdout)


class InvalidConfigTestcase(TinyCalTestCase):
    @property
    def calrc(self):
        return StringIO('''
col = 0
before = before?
after = -1
border = double
today.color = invalid:color
                ''')

    @property
    def args(self):
        return ['--border=single,full', '--color=always', '--today=2020/03/14', '--wk']

    def test_load_invalid_config(self):
        stdout = self.run_with_args([])
