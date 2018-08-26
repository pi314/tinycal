from __future__ import print_function

import argparse
import calendar
import sys

from argparse import Namespace
from datetime import date
from os.path import exists, expanduser


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


def parse_color_config(color_config):
    fg, bg = color_config.split(':')
    fg = fg.strip()
    bg = bg.strip()

    if fg.lower() == 'none' and bg.lower() == 'none':
        return ''

    color_codes = []

    if fg.lower() != 'none':
        if fg.upper() == fg:
            color_codes.append('1')

        color_codes.append('3' + COLOR_CODE[fg.lower()])

    color_codes.append('4' + COLOR_CODE[bg.lower()])

    ret = '\033['
    ret += ';'.join(color_codes)
    ret += 'm'

    return ret

    print(fg, bg)


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
        self.color = get('color', True)

        print(cfg)

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

        self.color_wk = '\033[1;30m' if self.color else ''
        self.color_today = parse_color_config(get('color_today', 'none:none')) if self.color else ''
        self.color_fill = '\033[1;30m' if self.color else ''


def read_user_config():
    calrc = ''
    calrc_2 = expanduser('~/.calrc')
    if exists(calrc_2):
        calrc = calrc_2

    calrc_1 = expanduser('~/.config/.calrc')
    if exists(calrc_1):
        calrc = calrc_1

    user_config = {}
    if calrc:
        with open(calrc) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                key, value = line.split('=')
                key = key.strip()
                value = value.strip()
                user_config[key.lower()] = value

    return user_config


def uncolor(color):
    return '\033[m' if color else ''


class TableYear(object):
    def __init__(self):
        self.months = []

    def add(self, m):
        self.months.append(m)

    def rows(self, col):
        ret = []
        buf = []
        for i in self.months:
            buf.append(i)
            if len(buf) == col:
                ret.append(tuple(buf))
                buf = []

        if buf:
            for i in range(col - len(buf)):
                dummy = TableMonth(None, None)
                buf.append(dummy)

            ret.append(tuple(buf))

        return ret


class TableMonth(object):
    def __init__(self, cal, m):
        if cal is None:
            self.empty = True
            self.weeks = []
            return

        self.empty = False
        self.year = m.year
        self.month = m.month
        self.title = m.strftime('%B') + ' ' + str(self.year)
        self.weeks = cal.monthdatescalendar(m.year, m.month)

        year_start = cal.monthdatescalendar(m.year, 1)[0][0]
        month_start = self.weeks[0][0]
        self.wk_start = int((month_start - year_start).days / 7)

    def set_render_config(self, config):
        self.config = config
        self.width = 7 * 2 + 6 + (3 if config.wk else 0)

    def render_title(self):
        if self.empty:
            return ' ' * self.width

        return '{title:^{width}}'.format(title=self.title, width=self.width)

    def render_week_ind(self):
        if self.empty:
            return ' ' * self.width

        ret = (self.config.color_wk + 'WK ' + uncolor(self.config.color_wk)) if self.config.wk else ''
        ret += ' '.join(d.strftime('%a')[:2] for d in self.weeks[0])
        return ret

    def render_week(self, wk):
        if wk >= len(self.weeks):
            return ' ' * self.width

        ret = ''
        if self.config.wk:
            ret = self.config.color_wk + str(self.wk_start + wk + 1).rjust(2) + ' ' + uncolor(self.config.color_wk)

        def day(d):
            if self.config.fill or d.month == self.month:
                color = ''

                if self.config.color:
                    if d == self.config.today:
                        color = self.config.color_today
                    elif d.month != self.month:
                        color = self.config.color_fill

                return color + str(d.day).rjust(2) + uncolor(color)

            return '  '

        ret += ' '.join(day(d) for d in self.weeks[wk])
        return ret


def render(config, table):
    for idx, row in enumerate(table.rows(config.col)):
        height = max(len(tm.weeks) for tm in row)
        lines = []

        for m in row:
            m.set_render_config(config)

        sep = ' | ' if config.sep else '  '
        lines.append(sep.join(m.render_title() for m in row))
        lines.append(sep.join(m.render_week_ind() for m in row))

        for wk in range(height):
            lines.append(sep.join(m.render_week(wk) for m in row))

        if idx > 0:
            sep = '-+-' if config.sep else '  '
            c = '-' if config.sep else ' '
            print(sep.join(c * m.width for m in row))

        for line in lines:
            print(line)


def main():
    parser = argparse.ArgumentParser(description='tiny cal')

    parser.add_argument('-c', nargs='?', dest='col', default=None, type=int,
            help='Column number.')

    parser.add_argument('-A', nargs='?', dest='after', default=None, type=int,
            help='Display the number of months after the current month.')

    parser.add_argument('-B', nargs='?', dest='before', default=None, type=int,
            help='Display the number of months before the current month.')

    parser.add_argument('-3', action='store_true', dest='a1b1', default=None,
            help='Equals to -A 1 -B 1.')

    parser.add_argument('-w', action='store_true', dest='wk', default=None,
            help='Display week number.')

    parser.add_argument('-s', action='store_true', dest='sep', default=None,
            help='Display separation line.')

    parser.add_argument('-f', action='store_true', dest='fill', default=None,
            help='Fill every month with previous/next month dates.')

    parser.add_argument('-C', action='store_false', dest='color', default=None,
            help='Disable VT100 color output.')

    parser.add_argument('year', type=int, nargs='?', default=None,
            help='Year to display.')

    parser.add_argument('month', type=int, nargs='?', default=None,
            help='Month to display. Must specified after year.')

    args = parser.parse_args()

    cfg = {}
    cfg.update(read_user_config())
    cli_cfg = vars(args)
    cli_cfg = {key: cli_cfg[key] for key in cli_cfg if cli_cfg[key] is not None}
    cfg.update(cli_cfg)

    config = TinyCalConfig(cfg)

    cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
    table = TableYear()

    for m in config.range:
        table.add(TableMonth(cal, m))

    render(config, table)


main()
