import calendar
import re
import sys

from calendar import Calendar, SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY
from datetime import date, timedelta
from os.path import exists, isfile

from . import CALRCS
from . import cli
from .color import Color
from .config import TinyCalConfig, Color
from .misc import DateCursor
from .misc import Tr
from .render import render_classic
from .table_struct import construct_table


class DateMark:
    def __init__(self, drange, color):
        self.drange = drange
        self.color = color

    def __contains__(self, item):
        if isinstance(item, date):
            if self.drange[0] == self.drange[1]:
                return item == self.drange[0]

            if self.drange[0] <= item and item <= self.drange[1]:
                return True

            if isinstance(item, tuple):
                return item[0] in self and item[1] in self

        return False

    def __repr__(self):
        return '{} ~ {} {}'.format(self.drange[0], self.drange[1], self.color)


def parse_marks_file(marks_file):
    if not marks_file or not exists(marks_file) or not isfile(marks_file):
        return []

    date_mark_fmt = re.compile(r'^(\d\d\d\d)/(\d\d)/(\d\d) ([a-zA-Z:]+)(.*)$')
    date_range_mark_fmt = re.compile(r'^(\d\d\d\d)/(\d\d)/(\d\d) ?[~-] ?(\d\d\d\d)/(\d\d)/(\d\d) ([a-zA-Z:]+)(.*)$')

    date_marks = []
    with open(marks_file) as f:
        for line in f:
            line = line.rstrip()

            m = date_mark_fmt.match(line)
            if m:
                d = date(*map(int, m.group(1, 2, 3)))
                color = Color(m.group(4))
                date_marks.append(DateMark((d, d), color))
                continue

            m = date_range_mark_fmt.match(line)
            if m:
                d1 = date(*map(int, m.group(1, 2, 3)))
                d2 = date(*map(int, m.group(4, 5, 6)))
                color = Color(m.group(7))
                date_marks.append(DateMark((d1, d2), color))
                continue

    for dm in date_marks:
        print(dm)

    return date_marks


def main():
    conf = TinyCalConfig.parse_conf(CALRCS)
    args = cli.parse_args()

    ''' Remove arguments that are not part of TinyCalConfig '''
    month = args.month
    delattr(args, 'month')

    year = args.year
    delattr(args, 'year')

    color_enable = {
            'never': False,
            'always': True,
            'auto': sys.stdout.isatty(),
            }.get(args.color, False)
    delattr(args, 'color')

    today = args.today or date.today()
    delattr(args, 'today')

    conf.merge(vars(args))

    cal = Calendar({
            'monday': MONDAY,
            'tuesday': TUESDAY,
            'wednesday': WEDNESDAY,
            'thursday': THURSDAY,
            'friday': FRIDAY,
            'saturday': SATURDAY,
            'sunday': SUNDAY}[conf.firstweekday])

    ''' Calculate display range '''
    if year is not None and month is not None:
        # given year, month
        drange = [
            DateCursor(cal, year, month, 1),
            DateCursor(cal, year, month, -1)
        ]

    elif year is not None and month is None:
        # given year
        drange = [
            DateCursor(cal, year, 1, 1),
            DateCursor(cal, year, 12, 31)
        ]

    else:
        drange = [
            DateCursor.from_date(cal, today),
            DateCursor.from_date(cal, today)
        ]

    ''' Apply before/after '''
    if conf.before:
        if conf.before.unit == 'W':
            drange[0] -= timedelta(weeks=conf.before.value)

        elif conf.before.unit == 'M':
            drange[0].move_back_n_month(conf.before.value)

    if conf.after:
        if conf.after.unit == 'W':
            drange[1] += timedelta(weeks=conf.after.value)

        elif conf.after.unit == 'M':
            drange[1].move_forward_n_month(conf.after.value)

    tr = Tr(conf.lang)

    cal_table = construct_table(conf, tr, cal, drange, today)

    if not color_enable:
        for name, field in vars(conf.__class__).items():
            if name.startswith('color_'):
                setattr(conf, name, Color(''))

        date_marks = tuple()

    else:
        date_marks = parse_marks_file(conf.marks)

    render_classic(conf, tr, cal_table, date_marks, today)
