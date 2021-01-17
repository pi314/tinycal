import unittest

import datetime
import re
import sys

from io import StringIO
from unittest.mock import patch, mock_open

from itertools import zip_longest
from os.path import join
from unicodedata import east_asian_width

from tinycal import tcal


def str_width(s):
    return sum(1 + (east_asian_width(c) in 'WF') for c in re.sub(r'\033\[[0-9;]*m', '', s))


def rjust(s, w):
    return s + (' ' * (w - str_width(s)))


class TinyCalTestCase(unittest.TestCase):
    @property
    def calrc(self):
        return {}

    def parse_answer_file(self, fname):
        args = []
        stdout = []

        with open(join('tests', fname)) as f:
            for line in f:
                line = line.rstrip('\n')
                if not line.startswith('#'):
                    stdout.append(line)
                    continue

                m = re.match(r'^# *\[args\] *(.*)$', line)
                if m:
                    args += m.group(1).split()

        return args, stdout

    @patch('sys.stderr', new_callable=StringIO)
    @patch('sys.stdout', new_callable=StringIO)
    def run_with_args(self, args, stdout, stderr):
        tcal.CALRCS = [self.calrc]
        sys.argv = ['tcal'] + args
        tcal.main()
        return stdout, stderr

    def check_output(self, args, answer, stdout):
        output = stdout.getvalue().rstrip('\n').split('\n')

        answer_width = max(map(str_width, answer))

        if answer != output:
            diff = '\n'
            diff += 'Args: ' + ' '.join(args) + '\n'
            diff += rjust('Expected:', answer_width) + ' // ' + 'Output:' '\n'
            for A, B in zip_longest(answer, output, fillvalue='\033[1;30m(~)\033[m'):
                if A != B:
                    sep_mark = '\033[1;31m<>\033[m'
                else:
                    sep_mark = '\033[1;32m//\033[m'

                diff += rjust(A, answer_width) + ' ' + sep_mark + ' ' + B + '\n'

            self.fail(diff)


# class NoBorderLayoutTestcase(TinyCalTestCase):
#     @property
#     def args(self):
#         return ['--border=none', '--color=never', '--today=2020/03/14', '--wk', '--fill']
#
#     def test_nofill_nowk(self):
#         stdout, stderr = self.run_with_args(['--no-wk', '--no-fill'])
#         self.check_output('border=none nofill nowk', stdout)
#
#     def test_1_month(self):
#         stdout, stderr = self.run_with_args([])
#         self.check_output('border=none', stdout)
#
#     def test_3_months(self):
#         stdout, stderr = self.run_with_args(['-3'])
#         self.check_output('border=none 3months', stdout)
#
#     def test_whole_year(self):
#         stdout, stderr = self.run_with_args(['2020'])
#         self.check_output('border=none 2020', stdout)
#
#
# class AsciiBorderLayoutTestcase(TinyCalTestCase):
#     def setUp(self):
#         self.border = 'ascii,full'
#
#     @property
#     def args(self):
#         return ['--border=' + self.border, '--color=never', '--today=2020/03/14', '--fill', '--wk']
#
#     def test_layout_nofill_nowk(self):
#         stdout, stderr = self.run_with_args(['--no-wk', '--no-fill'])
#         self.check_output('border=ascii nofill nowk', stdout)
#
#     def test_layout_basic(self):
#         self.border = 'ascii,basic'
#         stdout, stderr = self.run_with_args([])
#         self.check_output('border=ascii,basic', stdout)
#
#     def test_1_month(self):
#         stdout, stderr = self.run_with_args([])
#         self.check_output('border=ascii', stdout)
#
#     def test_3_months(self):
#         stdout, stderr = self.run_with_args(['-3'])
#         self.check_output('border=ascii 3months', stdout)
#
#     def test_whole_year(self):
#         stdout, stderr = self.run_with_args(['2020'])
#         self.check_output('border=ascii 2020', stdout)
#
#
# class SingleBorderLayoutTestcase(TinyCalTestCase):
#     def setUp(self):
#         self.border = 'single,full'
#
#     @property
#     def args(self):
#         return ['--border=' + self.border, '--color=never', '--today=2020/03/14', '--fill', '--wk']
#
#     def test_layout_nofill_nowk(self):
#         stdout, stderr = self.run_with_args(['--no-wk', '--no-fill'])
#         self.check_output('border=single nofill nowk', stdout)
#
#     def test_layout_basic(self):
#         self.border = 'single,basic'
#         stdout, stderr = self.run_with_args([])
#         self.check_output('border=single,basic', stdout)
#
#     def test_1_month(self):
#         stdout, stderr = self.run_with_args([])
#         self.check_output('border=single', stdout)
#
#     def test_3_months(self):
#         stdout, stderr = self.run_with_args(['-3'])
#         self.check_output('border=single 3months', stdout)
#
#     def test_whole_year(self):
#         stdout, stderr = self.run_with_args(['2020'])
#         self.check_output('border=single 2020', stdout)
#
#
# class DoubleBorderLayoutTestcase(TinyCalTestCase):
#     def setUp(self):
#         self.border = 'double,full'
#
#     @property
#     def args(self):
#         return ['--border=' + self.border, '--color=never', '--today=2020/03/14', '--fill', '--wk']
#
#     def test_layout_nofill_nowk(self):
#         stdout, stderr = self.run_with_args(['--no-wk', '--no-fill'])
#         self.check_output('border=double nofill nowk', stdout)
#
#     def test_layout_basic(self):
#         self.border = 'double,basic'
#         stdout, stderr = self.run_with_args([])
#         self.check_output('border=double,basic', stdout)
#
#     def test_1_month(self):
#         stdout, stderr = self.run_with_args([])
#         self.check_output('border=double', stdout)
#
#     def test_3_months(self):
#         stdout, stderr = self.run_with_args(['-3'])
#         self.check_output('border=double 3months', stdout)
#
#     def test_whole_year(self):
#         stdout, stderr = self.run_with_args(['2020'])
#         self.check_output('border=double 2020', stdout)


class WeekModeTestcase(TinyCalTestCase):
    # def test_1_month(self):
    #     stdout, stderr = self.run_with_args([])
    #     self.check_output('border=single', stdout)
    #
    # def test_3_months_nofill_nowk(self):
    #     stdout, stderr = self.run_with_args(['-3', '--no-fill', '--no-wk'])
    #     self.check_output('week 3months nofill nowk', stdout)
    #
    # def test_3_months(self):
    #     stdout, stderr = self.run_with_args(['-3'])
    #     self.check_output('week 3months', stdout)

    def test_week_across_year_first(self):
        args, expect = self.parse_answer_file('test_week_across_year_20200101')
        stdout, stderr = self.run_with_args(args)
        self.check_output(args, expect, stdout)

    def test_week_across_year_20191231(self):
        args, expect = self.parse_answer_file('test_week_across_year_20191231')
        stdout, stderr = self.run_with_args(args)
        self.check_output(args, expect, stdout)


# class WeldTestcase(TinyCalTestCase):
#     @property
#     def args(self):
#         return ['--border=single,noweld', '--color=never', '--today=2020/03/14', '--fill', '--wk']
#
#     def test_noweld(self):
#         stdout, stderr = self.run_with_args(['2020'])
#         self.check_output('noweld', stdout)
#
#
# class LangTestcase(TinyCalTestCase):
#     @property
#     def calrc(self):
#         return {}
#
#     @property
#     def args(self):
#         return ['--border=single', '--color=never', '--today=2020/03/14', '--fill', '--wk']
#
#     def test_en(self):
#         stdout, stderr = self.run_with_args(['--lang=en', '2020'])
#         self.check_output('border=single 2020', stdout)
#
#     def test_zh(self):
#         stdout, stderr = self.run_with_args(['--lang=zh', '2020'])
#         self.check_output('lang=zh', stdout)
#
#     def test_jp(self):
#         stdout, stderr = self.run_with_args(['--lang=jp', '2020'])
#         self.check_output('lang=jp', stdout)
#
#
# class ColorTestcase(TinyCalTestCase):
#     @property
#     def calrc(self):
#         return StringIO('''
# title.color = black:cyan
# wk.color = black:white
# today.color = black:white
# weekday.color = YELLOW
# weekday.sunday.color = GREEN
# weekday.saturday.color = GREEN
# sunday.color = RED
# saturday.color = RED
# border.color = magenta
# today.wk.color = white
# marks = MOCK_MARKS
#                 ''')
#
#     @property
#     def args(self):
#         return ['--border=single,full', '--color=always', '--today=2020/03/14', '--fill', '--wk']
#
#     def test_color(self):
#         def precise_mock_open(fname, *args, **kwargs):
#             if fname == 'MOCK_MARKS':
#                 return StringIO('''
# 2020/03/18 BLUE # comment
# 2020/03/19
# 2020/03/20 invalid:color
# ''')
#
#             else:
#                 return open(*args, **kwargs)
#
#         def precise_mock_exists(path):
#             if fname == 'MOCK_MARKS':
#                 return True
#
#             return False
#
#         with patch('builtins.open', new=precise_mock_open) as mock_file:
#             stdout, stderr = self.run_with_args([])
#
#         self.check_output('color', stdout)
#
#
# class InvalidConfigTestcase(TinyCalTestCase):
#     @property
#     def calrc(self):
#         return {
#                 'col': '0',
#                 'before': 'before?',
#                 'after': '-1',
#                 'border': 'double',
#                 'today.color': 'invalid:color',
#                 }
#
#     @property
#     def args(self):
#         return ['--border=single,full', '--color=always', '--today=2020/03/14', '--wk']
#
#     def test_load_invalid_config(self):
#         stdout = self.run_with_args([])
