"""
Parse configurations.
"""

from __future__ import print_function, absolute_import

import sys
from datetime import date
from argparse import Namespace
from calendar import SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY

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


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_config_with_type(cfg, key, default):
    if key not in cfg:
        return default

    try:
        if isinstance(default, bool) and not isinstance(cfg[key], bool):
            return {
                'false': False,
                'true': True,
                '0': False,
                '1': True,
            }[cfg[key].lower()]

        return type(default)(cfg[key])
    except:
        eprint('Warning: type incorrect of {} = {}'.format(key, cfg[key]))
        return default


def merge_color_config(base, new):
    b = list(map(str.strip, base.split(':') + ['']))
    n = list(map(str.strip, new.split(':') + ['']))

    b[0] = b[0] if b[0] else 'none'
    b[1] = b[1] if b[1] else 'none'
    n[0] = n[0] if n[0] else 'none'
    n[1] = n[1] if n[1] else 'none'

    if n[0].lower() != 'none':
        b[0] = n[0]

    if n[1].lower() != 'none':
        b[1] = n[1]

    return b[0] + ':' + b[1]


def parse_color_config(color_config):
    c = color_config.split(':') + ['none']
    fg = c[0].strip()
    bg = c[1].strip()

    fg = fg if fg else 'none'
    bg = bg if bg else 'none'

    if (not fg or fg.lower() == 'none') and (not bg or bg.lower() == 'none'):
        return ''

    if fg == 'none' and bg.lower() == 'white':
        fg = 'black'

    color_codes = []

    if fg.lower() != 'none':
        if fg.upper() == fg:
            color_codes.append('1')
        else:
            color_codes.append('0')

        color_codes.append('3' + COLOR_CODE[fg.lower()])

    if bg.lower() != 'none':
        color_codes.append('4' + COLOR_CODE[bg.lower()])

    ret = '\033['
    ret += ';'.join(color_codes)
    ret += 'm'

    return ret


class TinyCalConfig(Namespace):
    def __init__(self, cfg):
        def get(key, default):
            return get_config_with_type(cfg, key, default)

        today = date.today()
        self.today = today

        self.col = get('col', 3)
        self.after = get('after', 0)
        self.before = get('before', 0)
        self.wk = get('wk', False)
        self.sep = get('sep', True)
        self.fill = get('fill', False)
        self.year = get('year', today.year)
        self.month = get('month', today.month)
        self.border = get('border', True)
        self.lang = get('lang', 'zh')
        self.start_monday = get('start_monday', False)

        if cfg.get('a1b1'):
            self.after = 1
            self.before = 1

        if 'year' in cfg and 'month' not in cfg:
            year_month_range = [date(self.year, m, 1) for m in range(1, 13)]

        else:
            if 'year' in cfg and 'month' in cfg:
                base_date = date(self.year, self.month, 1)
            else:
                base_date = today

            year_month_range = [base_date]
            probe_y = base_date.year
            probe_m = base_date.month
            for i in range(self.before):
                probe_m -= 1
                if probe_m == 0:
                    probe_y -= 1
                    probe_m = 12

                year_month_range.append(date(probe_y, probe_m, 1))

            probe_y = base_date.year
            probe_m = base_date.month
            for i in range(self.after):
                probe_m += 1
                if probe_m == 13:
                    probe_y += 1
                    probe_m = 1

                year_month_range.append(date(probe_y, probe_m, 1))

        year_month_range.sort()
        self.range = year_month_range
        self.col = min(len(self.range), self.col)

        self.color = Namespace()
        self.color.enable = get('color', True)
        if self.color.enable:
            self.color.wk = parse_color_config(get('wk.color', 'BLACK'))
            self.color.fill = parse_color_config(get('fill.color', 'BLACK'))
            self.color.title = parse_color_config(get('title.color', ''))

            color_weekday_base = get('weekday.color', '')
            color_weekday_sun = merge_color_config(color_weekday_base, get('weekday.sunday.color', ''))
            color_weekday_mon = merge_color_config(color_weekday_base, get('weekday.monday.color', ''))
            color_weekday_tue = merge_color_config(color_weekday_base, get('weekday.tuesday.color', ''))
            color_weekday_wed = merge_color_config(color_weekday_base, get('weekday.wednesday.color', ''))
            color_weekday_thu = merge_color_config(color_weekday_base, get('weekday.thursday.color', ''))
            color_weekday_fri = merge_color_config(color_weekday_base, get('weekday.friday.color', ''))
            color_weekday_sat = merge_color_config(color_weekday_base, get('weekday.saturday.color', ''))
            self.color.weekday = {}
            self.color.weekday[BASE]      = parse_color_config(color_weekday_base)
            self.color.weekday[SUNDAY]    = parse_color_config(color_weekday_sun)
            self.color.weekday[MONDAY]    = parse_color_config(color_weekday_mon)
            self.color.weekday[TUESDAY]   = parse_color_config(color_weekday_tue)
            self.color.weekday[WEDNESDAY] = parse_color_config(color_weekday_wed)
            self.color.weekday[THURSDAY]  = parse_color_config(color_weekday_thu)
            self.color.weekday[FRIDAY]    = parse_color_config(color_weekday_fri)
            self.color.weekday[SATURDAY]  = parse_color_config(color_weekday_sat)

            color_day = {}
            color_day[SUNDAY]    = get('sunday.color', '')
            color_day[MONDAY]    = get('monday.color', '')
            color_day[TUESDAY]   = get('tuesday.color', '')
            color_day[WEDNESDAY] = get('wednesday.color', '')
            color_day[THURSDAY]  = get('thursday.color', '')
            color_day[FRIDAY]    = get('friday.color', '')
            color_day[SATURDAY]  = get('saturday.color', '')
            self.color.day = {}
            self.color.day[SUNDAY]    = parse_color_config(color_day[SUNDAY])
            self.color.day[MONDAY]    = parse_color_config(color_day[MONDAY])
            self.color.day[TUESDAY]   = parse_color_config(color_day[TUESDAY])
            self.color.day[WEDNESDAY] = parse_color_config(color_day[WEDNESDAY])
            self.color.day[THURSDAY]  = parse_color_config(color_day[THURSDAY])
            self.color.day[FRIDAY]    = parse_color_config(color_day[FRIDAY])
            self.color.day[SATURDAY]  = parse_color_config(color_day[SATURDAY])

            color_day_today = merge_color_config(
                    color_day[today.weekday()],
                    get('today.color', ':white'),
                    )
            self.color.today = parse_color_config(color_day_today)
        else:
            self.color.wk = ''
            self.color.fill = ''
            self.color.title = ''
            self.color.weekday = {}
            self.color.weekday[BASE]      = ''
            self.color.weekday[SUNDAY]    = ''
            self.color.weekday[MONDAY]    = ''
            self.color.weekday[TUESDAY]   = ''
            self.color.weekday[WEDNESDAY] = ''
            self.color.weekday[THURSDAY]  = ''
            self.color.weekday[FRIDAY]    = ''
            self.color.weekday[SATURDAY]  = ''
            self.color.day = {}
            self.color.day[SUNDAY]    = ''
            self.color.day[MONDAY]    = ''
            self.color.day[TUESDAY]   = ''
            self.color.day[WEDNESDAY] = ''
            self.color.day[THURSDAY]  = ''
            self.color.day[FRIDAY]    = ''
            self.color.day[SATURDAY]  = ''
            self.color.today = ''
