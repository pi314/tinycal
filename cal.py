import argparse
import calendar
from datetime import date
import sys


class Config(object):
    def __init__(self):
        self.col = 3
        self.after = 0
        self.before = 0
        self.wk = False
        self.sep = False
        self.fill = False
        self.color = True

    def update(self, args):
        if args.col is not None:
            self.col = args.col

        if args.wk is not None:
            self.wk = args.wk

        if args.sep is not None:
            self.sep = args.sep

        if args.fill is not None:
            self.fill = args.fill

        if args.color is not None:
            self.color = args.color

        if args.after is not None:
            self.after = args.after

        if args.before is not None:
            self.before = args.before

        if args.a1b1:
            self.after = 1
            self.before = 1

        today = date.today()
        self.today = today
        year_month_range = [today]

        probe_y = today.year
        probe_m = today.month
        for i in range(self.before):
            probe_m -= 1
            if probe_m == 0:
                probe_y -= 1
                probe_m = 12

            year_month_range.append(date(probe_y, probe_m, 1))

        probe_y = today.year
        probe_m = today.month
        for i in range(self.after):
            probe_m += 1
            if probe_m == 13:
                probe_y += 1
                probe_m = 1

            year_month_range.append(date(probe_y, probe_m, 1))

        year_month_range.sort()
        self.range = year_month_range


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
            ret.append(tuple(buf))

        return ret


class TableMonth(object):
    def __init__(self, cal, m):
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
        return '{title:^{width}}'.format(title=self.title, width=self.width)

    def render_week_ind(self):
        ret = 'WK ' if self.config.wk else ''
        ret += ' '.join(d.strftime('%a')[:2] for d in self.weeks[0])
        return ret

    def render_week(self, wk):
        if wk >= len(self.weeks):
            return ' ' * self.width

        ret = ''
        if self.config.wk:
            color = ''
            uncolor = ''
            if self.config.color:
                color = '\033[1;30m'
                uncolor = '\033[m'

            ret = color + str(self.wk_start + wk + 1).rjust(2) + uncolor + ' '

        def day(d):
            if self.config.fill or d.month == self.month:
                color = ''
                uncolor = ''

                if self.config.color:
                    if d == self.config.today:
                        color = '\033[0;30;47m'
                        uncolor = '\033[m'
                    elif d.month != self.month:
                        color = '\033[1;30m'
                        uncolor = '\033[m'

                return color + str(d.day).rjust(2) + uncolor

            return '  '

        ret += ' '.join(day(d) for d in self.weeks[wk])
        return ret


def render(config, table):
    for row in table.rows(config.col):
        height = max(len(tm.weeks) for tm in row)
        lines = []

        for m in row:
            m.set_render_config(config)

        sep = ' | ' if config.sep else '  '
        lines.append(sep.join(m.render_title() for m in row))
        lines.append(sep.join(m.render_week_ind() for m in row))

        for wk in range(height):
            lines.append(sep.join(m.render_week(wk) for m in row))

        for line in lines:
            print(line)

        print()


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

    args = parser.parse_args()

    config = Config()
    config.update(args)

    cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
    table = TableYear()

    for m in config.range:
        table.add(TableMonth(cal, m))

    render(config, table)


main()
