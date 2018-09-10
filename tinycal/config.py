"""
Parse configurations.
"""

from __future__ import print_function, absolute_import

import sys
import re
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
    r"""
    >>> p = parse_color_config
    >>> p('white:black')
    '\x1b[0;37;40m'

    No effect
    >>> p('')
    ''

    Keep background setting
    >>> p('white')
    '\x1b[0;37m'

    Keep foreground setting
    >>> p(':black')
    '\x1b[40m'

    Highlight
    >>> p('WHITE:black')
    '\x1b[1;37;40m'

    Reverse (NOTE: there is already an ASCII code 7 for reverse)
    >>> p(':white')
    '\x1b[0;30;47m'

    Equivalent configuration
    >>> assert p('white') == p('white:') == p('white:none')
    >>> assert p(':black') == p('none:black')
    >>> assert p(':white') == p('none:white') == p('NONE:white')

    Error handling
    >>> p('a:b:c')
    Traceback (most recent call last):
    ...
    Exception: invalid color configuration: a:b:c
    >>> p('a_1:')
    Traceback (most recent call last):
    ...
    Exception: unrecognized foreground color: a_1
    >>> p(':B')
    Traceback (most recent call last):
    ...
    Exception: unrecognized background color: b
    """
    patt = re.compile(r'^\s*(?P<fg>\w+)?\s*:?(?:\s*(?P<bg>\w+)\s*)?$')
    m = patt.match(color_config)
    if m is None:
        raise Exception('invalid color configuration: {}'.format(color_config))

    assert patt.match('').groups() == (None, None)
    assert patt.match('a').groups() == ('a', None)
    assert patt.match('a:').groups() == ('a', None)
    assert patt.match(':b').groups() == (None, 'b')
    assert patt.match('a:b').groups() == ('a', 'b')

    if m.group('fg') is None or m.group('fg').lower() == 'none':
        fg, bright = None, None
    else:
        fg = m.group('fg').lower()
        bright = '1' if fg.upper()==m.group('fg') else '0'  # highlight

    if m.group('bg') is None or m.group('bg').lower() == 'none':
        bg = None
    else:
        bg = m.group('bg').lower()

    if fg is not None and fg not in COLOR_CODE:
        raise Exception('unrecognized foreground color: {}'.format(fg))
    elif bg is not None and bg not in COLOR_CODE:
        raise Exception('unrecognized background color: {}'.format(bg))

    assert fg is None or fg in COLOR_CODE
    assert bg is None or bg in COLOR_CODE

    seq = lambda *t: '\033[{}m'.format(";".join(t))
    fg_code = lambda c: '3' + COLOR_CODE[c]
    bg_code = lambda c: '4' + COLOR_CODE[c]

    if fg is None:
        if bg is None:
            prefix =  ''
        elif bg == 'white':
            prefix =  seq('0', fg_code('black'), bg_code(bg))  # reverse
        else:
            prefix =  seq(bg_code(bg))  # keep foreground setting
    else:
        if bg is None:
            prefix =  seq(bright, fg_code(fg))  # keep background setting
        else:
            prefix =  seq(bright, fg_code(fg), bg_code(bg))
    return prefix


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
