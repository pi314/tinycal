"""
Parse configurations.
"""

from __future__ import print_function, absolute_import

import sys
import re
from datetime import date
from argparse import Namespace
from calendar import SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY

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


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


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
    r"""
    >>> merge_color_config('YELLOW', 'GREEN')
    'GREEN:none'
    >>> merge_color_config('YELLOW', '')
    'YELLOW:none'
    >>> merge_color_config('', 'RED')
    'RED:none'
    >>> merge_color_config('GREEN:none', 'RED')
    'RED:none'
    >>> merge_color_config('BLUE:YELLOW', ':RED')
    'BLUE:RED'
    """
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


parse_color_config = lambda color: color if isinstance(color, Color) else Color(color)
merge_color_config = lambda base, new: (base if isinstance(base, Color) else Color(base)) << Color(new)

class TinyCalConfig(Namespace):
    def __init__(self, cfg):
        def get(key, default):
            return get_config_with_type(cfg, key, default)

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
            # ignore `before` and `after` arguments and just list all months in the year
            year_month_range = [date(self.year, m, 1) for m in range(1, 13)]
        else:
            year_month_range = expand_year_month(self.before, self.after, self.year, self.month)

        self.matrix = to_matrix(year_month_range, self.col) if len(year_month_range) > self.col else [year_month_range]

        self.color = Namespace()
        self.color.enable = get('color', True)
        if self.color.enable:
            self.color.wk = parse_color_config(get('wk.color', 'BLACK'))
            self.color.fill = parse_color_config(get('fill.color', 'BLACK'))
            self.color.title = parse_color_config(get('title.color', ''))

            color_weekday_base = get('weekday.color', '')
            self.color.weekday = {
                BASE: parse_color_config(color_weekday_base),
                SUNDAY: parse_color_config(merge_color_config(color_weekday_base, get('weekday.sunday.color', ''))),
                MONDAY: parse_color_config(merge_color_config(color_weekday_base, get('weekday.monday.color', ''))),
                TUESDAY: parse_color_config(merge_color_config(color_weekday_base, get('weekday.tuesday.color', ''))),
                WEDNESDAY: parse_color_config(merge_color_config(color_weekday_base, get('weekday.wednesday.color', ''))),
                THURSDAY: parse_color_config(merge_color_config(color_weekday_base, get('weekday.thursday.color', ''))),
                FRIDAY: parse_color_config(merge_color_config(color_weekday_base, get('weekday.friday.color', ''))),
                SATURDAY: parse_color_config(merge_color_config(color_weekday_base, get('weekday.saturday.color', ''))),
                }

            self.color.day = {
                SUNDAY: parse_color_config(get('sunday.color', '')),
                MONDAY: parse_color_config(get('monday.color', '')),
                TUESDAY: parse_color_config(get('tuesday.color', '')),
                WEDNESDAY: parse_color_config(get('wednesday.color', '')),
                THURSDAY: parse_color_config(get('thursday.color', '')),
                FRIDAY: parse_color_config(get('friday.color', '')),
                SATURDAY: parse_color_config(get('saturday.color', '')),
                }

            self.color.today = parse_color_config(merge_color_config(self.color.day[today.weekday()], get('today.color', ':white')))
        else:
            self.color.wk = ''
            self.color.fill = ''
            self.color.title = ''
            self.color.weekday = dict.fromkeys([BASE, SUNDAY, MONDAY, TUESDAY, WEDNESDAY, TUESDAY, FRIDAY, SATURDAY], '')
            self.color.day = dict.fromkeys([SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY], '')
            self.color.today = ''


today = date.today()
