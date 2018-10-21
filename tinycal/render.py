# -*- coding: utf-8 -*-

"""
Render calendar.
"""

from datetime import date
from calendar import Calendar, SUNDAY, MONDAY

from .config import Color


today = date.today()

LANG = {
        'jp': ['月', '火', '水', '木', '金', '土', '日'],
        'zh': ['一', '二', '三', '四', '五', '六', '日'],
        'en': ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'],
        'lower': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
        }


def expand_year_month(before, after, year, month):
    r"""
    >>> expand_year_month(1, 1, 2018, 1)
    [datetime.date(2017, 12, 1), datetime.date(2018, 1, 1), datetime.date(2018, 2, 1)]
    """
    return [date(year - (month <= i), (month - 1 - i) % 12 + 1, 1) for i in range(before, 0, -1)] + \
           [date(year, month, 1)] + \
           [date(year + (month + i > 12), (month - 1 + i) % 12 + 1, 1) for i in range(1, after+1)]


class TinyCal(object):
    def __init__(self, conf, args):
        "conclude todo base on `config` and `args`, and set todo as property"

        # `conf` -- updated by `args`
        for k in vars(conf):
            if k in vars(args) and getattr(args, k) is not None:
                setattr(conf, k , getattr(args, k))
        self.conf = conf

        # `months`
        from collections import namedtuple

        calendar = Calendar(MONDAY if conf.start_monday else SUNDAY)
        monthdates = calendar.monthdatescalendar

        if args.year is not None and args.month is None:
            first_month_dates = [date(args.year, month, 1) for month in range(1, 13)]
        else:
            year = args.year or today.year
            month = args.month or today.month
            before, after = (1, 1) if args.a1b1 else (conf.before, conf.after)
            first_month_dates = expand_year_month(before, after, year, month)

        def get_wks(fdt):
            wk_start = (monthdates(fdt.year, fdt.month)[0][0] - monthdates(fdt.year, 1)[0][0]).days // 7 + 1
            return list(range(wk_start, wk_start + len(monthdates(fdt.year, fdt.month))))

        Month = namedtuple('Month', ['title', 'wks', 'weeks'])
        Day = namedtuple('Day', ['date', 'filled'])

        self.months = [
                Month(
                    title = fdt.strftime('%B %Y'),
                    wks = get_wks(fdt),
                    weeks = [[Day(date=dt, filled=(dt.month != fdt.month)) for dt in row]
                             for row in monthdates(fdt.year, fdt.month)],
                    )
                for fdt in first_month_dates
                ]

        # `cell_width`
        self.cell_width = 7 * 2 + 6 + (3 if conf.wk else 0)

        # enable/disable coloring
        if not args.color:
            for k in vars(conf):
                if k.startswith('color_'):
                    setattr(conf, k, Color(''))

        # `render_title`
        self.render_title = lambda title: conf.color_title('{:^{}}'.format(title, self.cell_width))

        # `render_wk`
        if conf.wk:
            self.render_wk = lambda wk: [conf.color_wk('%2s' % wk)]
        else:
            self.render_wk = lambda wk: []

        # `render_day`
        def render_day(day):
            if day.filled:
                if conf.fill:
                    c = conf.color_fill
                else:
                    c = lambda s: '  '
            else:
                if day.date == today:
                    c = conf.color_today
                else:
                    c = getattr(conf, 'color_%s' % LANG['lower'][day.date.weekday()])
            return c('{:2}'.format(day.date.day))

        self.render_week = lambda week: list(map(render_day, week))

        # `render_weekdays`
        def render_weekday(idx):
            color_name = 'color_weekday_%s' % LANG['lower'][idx]
            color = getattr(conf, color_name)
            string = LANG[conf.lang][idx]
            return color(string) + conf.color_weekday.code if color else string

        if conf.wk:
            self.render_weekdays = lambda: conf.color_wk('WK') + conf.color_weekday(
                    ' ' + ' '.join(map(render_weekday, calendar.iterweekdays()))
                    )
        else:
            self.render_weekdays = lambda: conf.color_weekday(
                    ' '.join(map(render_weekday, calendar.iterweekdays()))
                    )

    @property
    def colored(self):
        return [
            [self.render_title(title), self.render_weekdays()] + [
                ' '.join(self.render_wk(wk) + self.render_week(week))
                for wk, week in zip(wks, weeks)
                ]
            for title, wks, weeks in self.months
            ]

    @property
    def framed(self):
        try:
            from itertools import zip_longest
        except:
            from itertools import izip_longest as zip_longest

        def to_matrix(seq, col, dummy):
            if len(seq) > col:
                return [seq[:col]] + to_matrix(seq[col:], col, dummy)
            else:
                return [seq + [dummy] * (col - len(seq))]

        col = min(self.conf.col, len(self.months))

        if self.conf.sep:
            sep_v = ' | '
            sep_h_int = '-+-'
            sep_h_line = '-'
        else:
            sep_v = '  '
            sep_h_int = '  '
            sep_h_line = ' '

        sep_h = sep_h_int.join([sep_h_line * self.cell_width] * col)

        if self.conf.border:
            top = ('.-' + ('-' * len(sep_h)) + '-.')
            bottom = ("'-" + ('-' * len(sep_h)) + "-'")

            wrap = lambda lines: [top] + lines + [bottom]
            left, right = '| ', ' |'
            hr = ('|' + sep_h[0] + sep_h + sep_h[0] + '|')
        else:
            wrap = lambda lines: lines
            left = right = ''
            hr = sep_h

        matrix = to_matrix(self.colored, col, [])

        lines_of_rows = [
                [left + sep_v.join(slices) + right for slices in zip_longest(*row, fillvalue=' ' * self.cell_width)]
                for row in matrix
                ]
        framed_lines = wrap(sum(([hr] + lines for lines in lines_of_rows[1:]), lines_of_rows[0]))
        return framed_lines

    def render(self):
        return '\n'.join(self.framed)
