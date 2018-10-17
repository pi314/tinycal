"""
Parse configurations.
"""

from __future__ import print_function, absolute_import

import sys
import re
from datetime import date
from argparse import Namespace
from calendar import SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, Calendar

from .config2 import Color


COLOR_CODE = {
    'black': '0',
    'red': '1',
    'green': '2',
    'yellow': '3',
    'blue': '4',
    'magenta': '5',
    'cyan': '6',
    'white': '7',
    }
BASE = max(SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY) + 1


def to_matrix(L, c):
    r"""
    >>> L = [1, 2, 3, 4, 5, 6, 7]
    >>> to_matrix(L, 2)
    [[1, 2], [3, 4], [5, 6], [7, None]]
    >>> to_matrix(L, 3)
    [[1, 2, 3], [4, 5, 6], [7, None, None]]
    >>> to_matrix(L, 4)
    [[1, 2, 3, 4], [5, 6, 7, None]]
    >>> to_matrix(L, 7)
    [[1, 2, 3, 4, 5, 6, 7]]
    >>> to_matrix(L, 8)
    [[1, 2, 3, 4, 5, 6, 7, None]]
    """
    return [L[i:i+c] + [None] * (i + c - len(L)) for i in range(0, len(L), c)]


def expand_year_month(before, after, year, month):
    return [date(year - (month <= i), (month - 1 - i) % 12 + 1, 1) for i in range(1, before+1)][::-1] + \
           [date(year, month, 1)] + \
           [date(year + (month + i > 12), (month - 1 + i) % 12 + 1, 1) for i in range(1, after+1)]


class TinyCalConfig(Namespace):
    def __init__(self, cfg):
        self.wk = cfg.get('wk', False)
        self.sep = cfg.get('sep', True)
        self.fill = cfg.get('fill', False)
        self.border = cfg.get('border', True)

        # cal -- may enhance to collect more logic
        # ========================================

        firstweekday = MONDAY if cfg.get('start_monday', False) else SUNDAY
        self.cal = Calendar(firstweekday)

        # lang -- weekday lang
        # ====================

        self.lang = cfg.get('lang', 'zh')

        # today -- may be colored
        # =======================

        self.today = today

        # matrix
        # ======

        col = cfg.get('col', 3)
        after = cfg.get('after', 0)
        before = cfg.get('before', 0)
        year = cfg.get('year', today.year)
        month = cfg.get('month', today.month)
        if cfg.get('a1b1'):
            after = 1
            before = 1

        if 'year' in cfg and 'month' not in cfg:
            # ignore `before` and `after` arguments and just list all months in the year
            year_month_range = [date(year, m, 1) for m in range(1, 13)]
        else:
            year_month_range = expand_year_month(before, after, year, month)

        self.matrix = to_matrix(year_month_range, col) if len(year_month_range) > col else [year_month_range]

        # color
        # =====

        self.color = Namespace()
        self.color.enable = cfg.get('color', True)  # from args
        if self.color.enable:
            self.color.wk = Color(cfg.get('wk.color', 'BLACK'))
            self.color.fill = Color(cfg.get('fill.color', 'BLACK'))
            self.color.title = Color(cfg.get('title.color', ''))

            color_weekday_base = Color(cfg.get('weekday.color', ''))
            self.color.weekday = {
                BASE: color_weekday_base,
                SUNDAY: color_weekday_base << Color(cfg.get('weekday.sunday.color', '')),
                MONDAY: color_weekday_base << Color(cfg.get('weekday.monday.color', '')),
                TUESDAY: color_weekday_base << Color(cfg.get('weekday.tuesday.color', '')),
                WEDNESDAY: color_weekday_base << Color(cfg.get('weekday.wednesday.color', '')),
                THURSDAY: color_weekday_base << Color(cfg.get('weekday.thursday.color', '')),
                FRIDAY: color_weekday_base << Color(cfg.get('weekday.friday.color', '')),
                SATURDAY: color_weekday_base << Color(cfg.get('weekday.saturday.color', '')),
                }

            self.color.day = {
                SUNDAY: Color(cfg.get('sunday.color', '')),
                MONDAY: Color(cfg.get('monday.color', '')),
                TUESDAY: Color(cfg.get('tuesday.color', '')),
                WEDNESDAY: Color(cfg.get('wednesday.color', '')),
                THURSDAY: Color(cfg.get('thursday.color', '')),
                FRIDAY: Color(cfg.get('friday.color', '')),
                SATURDAY: Color(cfg.get('saturday.color', '')),
                }

            self.color.today = self.color.day[today.weekday()] << Color(cfg.get('today.color', ':white'))
        else:
            self.color.wk = Color('')
            self.color.fill = Color('')
            self.color.title = Color('')
            self.color.weekday = dict.fromkeys([BASE, SUNDAY, MONDAY, TUESDAY, WEDNESDAY, TUESDAY, FRIDAY, SATURDAY], Color(''))
            self.color.day = dict.fromkeys([SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY], Color(''))
            self.color.today = Color('')


today = date.today()
