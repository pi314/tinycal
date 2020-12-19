import sys

import calendar

from calendar import Calendar, SUNDAY, MONDAY
from datetime import date, timedelta

from . import CALRCS
from . import cli
from .config import TinyCalConfig, Color


def number_of_days_in_month(year, month):
    return calendar.monthrange(year, month)[1]


class Date(date):
    def __new__(cls, *args, **kwargs):
        # Source: https://stackoverflow.com/a/45981230/3812388
        # because __new__ creates the instance you need to pass the arguments
        # to the superclass here and **not** in the __init__
        if len(args) == 1 and isinstance(args[0], date):
            d = args[0]
            return super().__new__(cls, year=d.year, month=d.month, day=d.day)

        else:
            return super().__new__(cls, *args, **kwargs)

    def __int__(self):
        return (self.year * 12) + (self.month - 1)

    @staticmethod
    def from_um(um):
        return {'year': um // 12, 'month': (um % 12) + 1}

    def __sub__(self, other):
        if isinstance(other, MonthDelta):
            um = int(self) - int(other)
            return Date(**Date.from_um(um), day=self.day)

        return super().__sub__(other)

    def __add__(self, other):
        if isinstance(other, MonthDelta):
            um = int(self) + int(other)
            return Date(**Date.from_um(um), day=self.day)

        return super().__add__(other)

    @staticmethod
    def closed_range(a, b):
        for i in range(int(a), int(b) + 1):
            yield Date(**Date.from_um(i), day=1)

    def week_num(self, cal):
        return (self - cal.monthdatescalendar(self.year, 1)[0][0]).days // 7 + 1

    def week_first_day(self, cal):
        return self - timedelta(days=list(cal.iterweekdays()).index(self.weekday()))

    def week_last_day(self, cal):
        return self + timedelta(days=6 - list(cal.iterweekdays()).index(self.weekday()))


class MonthDelta:
    def __init__(self, months):
        self.months = months

    def __int__(self):
        return self.months


def main():
    conf = TinyCalConfig.parse_conf(CALRCS)
    args = cli.parse_args()

    print(conf)
    print()

    print(args)
    print()

    # Remove arguments that are no part of TinyCalConfig
    month = args.month
    delattr(args, 'month')

    year = args.year
    delattr(args, 'year')

    color = args.color
    delattr(args, 'color')

    today = Date(args.today or date.today())
    delattr(args, 'today')

    conf.merge(vars(args))
    print(conf)
    print()

    cal = Calendar(MONDAY if conf.start_monday else SUNDAY)
    monthdates = cal.monthdatescalendar

    # Calculate display range
    if year is not None and month is not None:
        # given year, month
        display_range_start = Date(year, month, 1)
        display_range_end = Date(year, month, number_of_days_in_month(year, month))

    elif year is not None and month is None:
        # given year
        display_range_start = Date(year, 1, 1)
        display_range_end = Date(year, 12, 31)

    else:
        display_range_start = today
        display_range_end = today

    # Apply before/after
    if conf.before:
        if conf.before.unit == 'W':
            display_range_start -= timedelta(weeks=conf.before.value)

        elif conf.before.unit == 'M':
            display_range_start -= MonthDelta(conf.before.value)

    if conf.after:
        if conf.after.unit == 'W':
            display_range_end += timedelta(weeks=conf.after.value)

        elif conf.after.unit == 'M':
            display_range_end += MonthDelta(conf.after.value)

    print('start =', display_range_start)
    print('today =', today)
    print('end =  ', display_range_end)
    print()

    if not conf.cont:
        for m in Date.closed_range(display_range_start, display_range_end):
            print(m.year, m.month)
            print('WK', ' '.join(map(lambda x: ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su', 'WK'][x], cal.iterweekdays())))
            for week in monthdates(m.year, m.month):
                wk = Date(week[0]).week_num(cal)
                print(str(wk).rjust(2), ' '.join(str(day.day).rjust(2) for day in week))

            print()

    else:
        print('cont')
        print('start =', display_range_start.week_first_day(cal))
        print('end =  ', display_range_end.week_last_day(cal))
