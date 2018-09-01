from __future__ import print_function

import calendar
import sys

from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
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

JAPANESE_WEEKDAY = '月火水木金土日'

CALRC_1ST = '~/.config/.calrc'
CALRC_2ND = '~/.calrc'


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

    if n[0] and n[0].lower() != 'none':
        b[0] = n[0]

    if n[1] and n[1].lower() != 'none':
        b[1] = n[1]

    return b[0] + ':' + b[1]


def parse_color_config(color_config):
    c = color_config.split(':') + ['none']
    fg = c[0].strip()
    bg = c[1].strip()

    if (not fg or fg.lower() == 'none') and (not bg or bg.lower() == 'none'):
        return ''

    color_codes = []

    if fg and fg.lower() != 'none':
        if fg.upper() == fg:
            color_codes.append('1')
        else:
            color_codes.append('0')

        color_codes.append('3' + COLOR_CODE[fg.lower()])

    if bg and bg.lower() != 'none':
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
        self.jp = get('jp', False)
        self.start_monday = get('start_monday', False)

        self.color = Namespace()
        self.color.enable = get('color', True)

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

        if self.color.enable:
            self.color.wk = parse_color_config(get('color.wk', 'BLACK'))
            self.color.today = parse_color_config(get('color.today', 'black:white'))
            self.color.fill = parse_color_config(get('color.fill', 'BLACK'))
            self.color.title = parse_color_config(get('color.title', ''))

            self.color.weekday = Namespace()
            color_base = get('color.weekday', '')
            color_sun = merge_color_config(color_base, get('color.weekday.sunday', ''))
            color_mon = merge_color_config(color_base, get('color.weekday.monday', ''))
            color_tue = merge_color_config(color_base, get('color.weekday.tuesday', ''))
            color_wed = merge_color_config(color_base, get('color.weekday.wednesday', ''))
            color_thu = merge_color_config(color_base, get('color.weekday.thursday', ''))
            color_fri = merge_color_config(color_base, get('color.weekday.friday', ''))
            color_sat = merge_color_config(color_base, get('color.weekday.saturday', ''))
            self.color.weekday.base = parse_color_config(color_base)
            self.color.weekday.sun = parse_color_config(color_sun)
            self.color.weekday.mon = parse_color_config(color_mon)
            self.color.weekday.tue = parse_color_config(color_tue)
            self.color.weekday.wed = parse_color_config(color_wed)
            self.color.weekday.thu = parse_color_config(color_thu)
            self.color.weekday.fri = parse_color_config(color_fri)
            self.color.weekday.sat = parse_color_config(color_sat)
        else:
            self.color.wk = ''
            self.color.today = ''
            self.color.fill = ''
            self.color.title = ''
            self.color.weekday = Namespace()
            self.color.weekday.base = ''
            self.color.weekday.sun = ''
            self.color.weekday.mon = ''
            self.color.weekday.tue = ''
            self.color.weekday.wed = ''
            self.color.weekday.thu = ''
            self.color.weekday.fri = ''
            self.color.weekday.sat = ''


def read_user_config():
    calrc = ''
    calrc_2 = expanduser(CALRC_2ND)
    if exists(calrc_2):
        calrc = calrc_2

    calrc_1 = expanduser(CALRC_1ST)
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


def color(s, c):
    return c + s + ('\033[m' if c else '')


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

        return color('{title:^{width}}'.format(
            title=self.title,
            width=self.width
        ),
        self.config.color.title)

    def render_weekday(self):
        if self.empty:
            return ' ' * self.width

        ret = color('WK', self.config.color.wk) if self.config.wk else ''

        ret += self.config.color.weekday.base
        ret += ' ' if self.config.wk else ''

        def render_single_weekday(d):
            c = {
                calendar.SUNDAY: self.config.color.weekday.sun,
                calendar.MONDAY: self.config.color.weekday.mon,
                calendar.TUESDAY: self.config.color.weekday.tue,
                calendar.WEDNESDAY: self.config.color.weekday.wed,
                calendar.THURSDAY: self.config.color.weekday.thu,
                calendar.FRIDAY: self.config.color.weekday.fri,
                calendar.SATURDAY: self.config.color.weekday.sat,
            }[d.weekday()]
            if self.config.jp:
                ret = color(JAPANESE_WEEKDAY[d.weekday()], c)
            else:
                ret = color(d.strftime('%a')[:2], c)
            return ret + (self.config.color.weekday.base if c else '')

        ret += ''.join([
            ' '.join(
                render_single_weekday(d)
                for d in self.weeks[0]
            ),
        ])

        ret += '\033[m' if self.config.color.weekday.base else ''
        return ret

    def render_week(self, wk):
        if wk >= len(self.weeks):
            return ' ' * self.width

        ret = ''
        if self.config.wk:
            ret = ''.join([
                self.config.color.wk,
                str(self.wk_start + wk + 1).rjust(2),
                uncolor(self.config.color.wk),
                ' '
            ])

        def day(d):
            if self.config.fill or d.month == self.month:
                color = ''

                if self.config.color:
                    if d == self.config.today:
                        color = self.config.color.today
                    elif d.month != self.month:
                        color = self.config.color.fill

                return color + str(d.day).rjust(2) + uncolor(color)

            return '  '

        ret += ' '.join(day(d) for d in self.weeks[wk])
        return ret


def render(config, table):
    rows = table.rows(config.col)

    for row in rows:
        for m in row:
            m.set_render_config(config)

    max_row = len(rows) - 1
    sep_v = ' | ' if config.sep else '  '
    sep_h_int = '-+-' if config.sep else '  '
    sep_h_line = '-' if config.sep else ' '
    sep_h = sep_h_int.join(sep_h_line * m.width for m in rows[0])

    for idx, row in enumerate(rows):
        height = max(len(tm.weeks) for tm in row)
        lines = []

        for m in row:
            m.set_render_config(config)

        lines.append(sep_v.join(m.render_title() for m in row))
        lines.append(sep_v.join(m.render_weekday() for m in row))

        for wk in range(height):
            lines.append(sep_v.join(m.render_week(wk) for m in row))

        if idx == 0 and config.border:
            print('.-' + ('-' * len(sep_h)) + '-.')

        if idx > 0:
            print(('|' + sep_h[0] if config.border else '') + sep_h + (sep_h[0] + '|' if config.border else ''))

        for line in lines:
            print(('| ' if config.border else '') + line + (' |' if config.border else ''))

        if idx == max_row and config.border:
            print("'-" + ('-' * len(sep_h)) + "-'")


def main():
    parser = ArgumentParser(
            description='tinycal: Python implementation of cal utility.',
            epilog='\n'.join((
                'Configuration files:',
                '1st: {}'.format(CALRC_1ST),
                '2nd: {}'.format(CALRC_2ND),
                )),
            formatter_class=RawTextHelpFormatter,
            )

    parser.add_argument('--col', dest='col', default=None, type=int,
            help='Specify the column numbers.')

    parser.add_argument('-A', dest='after', default=None, type=int,
            help='Display the number of months after the current month.')

    parser.add_argument('-B', dest='before', default=None, type=int,
            help='Display the number of months before the current month.')

    parser.add_argument('-3', action='store_true', dest='a1b1', default=None,
            help='Equals to -A 1 -B 1.')

    parser.add_argument('-w', action='store_true', dest='wk', default=None,
            help='Display week number.')
    parser.add_argument('-W', action='store_false', dest='wk', default=None,
            help='Don`t display week number.')

    parser.add_argument('-s', '--sep', action='store_true', dest='sep', default=None,
            help='Display separation lines.')
    parser.add_argument('-S', '--no-sep', action='store_false', dest='sep', default=None,
            help='Don`t display separation lines.')

    parser.add_argument('-b', '--border', action='store_true', dest='border', default=None,
            help='Display border lines.')
    parser.add_argument('-nb', '--no-border', action='store_false', dest='border', default=None,
            help='Don`t display border lines.')

    parser.add_argument('-f', '--fill', action='store_true', dest='fill', default=None,
            help='Fill every month into rectangle with previous/next month dates.')
    parser.add_argument('-F', '--no-fill', action='store_false', dest='fill', default=None,
            help='Don`t fill month into rectangle.')

    parser.add_argument('-c', action='store_true', dest='color', default=None,
            help='Enable VT100 color output.')
    parser.add_argument('-C', action='store_false', dest='color', default=None,
            help='Disable VT100 color output.')

    parser.add_argument('-j', action='store_true', dest='jp', default=None,
            help='Enable Japanese weekday names.')
    parser.add_argument('-J', action='store_false', dest='jp', default=None,
            help='Disable Japanese weekday names.')

    parser.add_argument('-m', action='store_true', dest='start_monday', default=None,
            help='Use Monday as first weekday.')
    parser.add_argument('-M', action='store_false', dest='start_monday', default=None,
            help='Use Sunday as first weekday.')

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

    cal = calendar.Calendar(firstweekday=calendar.MONDAY if config.start_monday else calendar.SUNDAY)
    table = TableYear()

    for m in config.range:
        table.add(TableMonth(cal, m))

    render(config, table)


if __name__ == '__main__':
    main()
