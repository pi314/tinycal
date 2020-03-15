import unittest

import datetime

from io import StringIO
from unittest.mock import patch
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
    def expect_output(self, args, answer_file, stdout):
        tcal.CALRCS = [self.calrc]
        tcal.main(self.args + args)
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
        self.expect_output(['--no-wk', '--no-fill'], 'border=off nofill nowk')

    def test_1_month(self):
        self.expect_output([], 'border=off')

    def test_3_months(self):
        self.expect_output(['-3'], 'border=off 3months')

    def test_whole_year(self):
        self.expect_output(['2020'], 'border=off 2020')


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
        self.expect_output(['--no-wk', '--no-fill'], 'border=ascii nofill nowk')

    def test_layout_basic(self):
        self.border = 'ascii,basic'
        self.expect_output([], 'border=ascii,basic')

    def test_1_month(self):
        self.expect_output([], 'border=ascii')

    def test_3_months(self):
        self.expect_output(['-3'], 'border=ascii 3months')

    def test_whole_year(self):
        self.expect_output(['2020'], 'border=ascii 2020')


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
        self.expect_output(['--no-wk', '--no-fill'], 'border=single nofill nowk')

    def test_layout_basic(self):
        self.border = 'single,basic'
        self.expect_output([], 'border=single,basic')

    def test_1_month(self):
        self.expect_output([], 'border=single')

    def test_3_months(self):
        self.expect_output(['-3'], 'border=single 3months')

    def test_whole_year(self):
        self.expect_output(['2020'], 'border=single 2020')


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
        self.expect_output(['--no-wk', '--no-fill'], 'border=double nofill nowk')

    def test_layout_basic(self):
        self.border = 'double,basic'
        self.expect_output([], 'border=double,basic')

    def test_1_month(self):
        self.expect_output([], 'border=double')

    def test_3_months(self):
        self.expect_output(['-3'], 'border=double 3months')

    def test_whole_year(self):
        self.expect_output(['2020'], 'border=double 2020')


class ContiguousModeTestcase(TinyCalTestCase):
    @property
    def calrc(self):
        return StringIO('')

    @property
    def args(self):
        return ['--border=single', '--color=never', '--today=2020/03/14', '--fill', '--wk', '--cont']

    def test_1_month(self):
        self.expect_output([], 'border=single')

    def test_3_months_nofill_nowk(self):
        self.expect_output(['-3', '--no-fill', '--no-wk'], 'cont 3months nofill nowk')

    def test_3_months(self):
        self.expect_output(['-3'], 'cont 3months')


class LangTestcase(TinyCalTestCase):
    @property
    def calrc(self):
        return StringIO('')

    @property
    def args(self):
        return ['--border=single', '--color=never', '--today=2020/03/14', '--fill', '--wk']

    def test_en(self):
        self.expect_output(['--lang=en', '2020'], 'border=single 2020')

    def test_zh(self):
        self.expect_output(['--lang=zh', '2020'], 'lang=zh')

    def test_jp(self):
        self.expect_output(['--lang=jp', '2020'], 'lang=jp')

    def test_jp_cont(self):
        self.expect_output(['--lang=jp', '--cont', '2020'], 'lang=jp cont')


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
                ''')

    @property
    def args(self):
        return ['--border=single,full', '--color=always', '--today=2020/03/14', '--fill', '--wk']

    def test_color(self):
        self.expect_output([], 'color')
