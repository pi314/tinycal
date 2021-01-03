import sys

import calendar

from calendar import Calendar, SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY
from datetime import date, timedelta

from . import CALRCS
from . import cli
from .config import TinyCalConfig, Color
from .render import render_classic
from .table_struct import construct_table
from .misc import Tr
from .misc import DateCursor


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

    render_classic(conf, tr, cal_table, drange, today)
