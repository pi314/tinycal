# -*- coding: utf-8 -*-

"""
Render calendar.
"""

from calendar import SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY

BASE = max(SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY) + 1


class TinyCal(object):
    def __init__(self, config, args):
        "conclude todo base on `config` and `args`, and set todo as property"
        self.config = config

        self.border = config.border
        self.sep = config.sep
        self.matrix = config.matrix
        self.wk = config.wk
        self.cell_width = 7 * 2 + 6 + (3 if self.wk else 0)

        self.weekdays = list(config.cal.iterweekdays())

        # ==== title ====

        self.render_title = lambda title: self.config.color.title('{:^{}}'.format(title, self.cell_width))

        # ==== weekdays ====

        from calendar import day_name

        BUILTIN_WEEKDAY = [day_name[i][:2] for i in range(7)]
        JAPANESE_WEEKDAY = ['月', '火', '水', '木', '金', '土', '日']
        CHINESE_WEEKDAY = ['一', '二', '三', '四', '五', '六', '日']
        ENGLISH_WEEKDAY = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']

        if self.config.lang == 'jp':
            lang = lambda wd: JAPANESE_WEEKDAY[wd]
        elif self.config.lang == 'zh':
            lang = lambda wd: CHINESE_WEEKDAY[wd]
        else:
            lang = lambda wd: BUILTIN_WEEKDAY[wd]

        def render_single_weekday(wd):
            c = config.color.weekday[wd]
            c2 = lambda s: c(s)+config.color.weekday[BASE].code if c else s
            return c2(lang(wd))

        half_colored_weekdays = ' '.join(render_single_weekday(wd) for wd in self.weekdays)
        self.colored_weekdays = config.color.wk('WK') + config.color.weekday[BASE](' ' + half_colored_weekdays) \
                                if config.wk else \
                                config.color.weekday[BASE](half_colored_weekdays)

    def month(self, dt):
        "date -> {'title', 'weekdays', 'weeks': [[date]]}"

    @property
    def colored(self):
        def render_single_day(month, dt):
            if dt.month != month:
                if self.config.fill:
                    c = self.config.color.fill
                else:
                    c = lambda s: '  '
            else:
                if dt == self.config.today:
                    c = self.config.color.today
                else:
                    c = self.config.color.day[dt.weekday()]
            return c('{:2}'.format(dt.day))

        L = []
        for dt in self.config.list:
            colored_month = []

            title = '%s %s' % (dt.strftime('%B'), dt.year)

            weeks = self.config.cal.monthdatescalendar(dt.year, dt.month)

            year_start = self.config.cal.monthdatescalendar(dt.year, 1)[0][0]
            month_start = weeks[0][0]
            wk_start = (month_start - year_start).days // 7 + 1
            wks = list(range(wk_start, wk_start+len(weeks)))

            if self.config.wk:
                colored_wk = lambda wk: [self.config.color.wk('{:2}'.format(wk))]
            else:
                colored_wk = lambda wk: []

            colored_month.append(self.render_title(title))
            colored_month.append(self.colored_weekdays)
            for wk, week in zip(wks, weeks):
                colored_week = ' '.join(colored_wk(wk) + [render_single_day(dt.month, sdt) for sdt in week])
                colored_month.append(colored_week)

            L.append(colored_month)
        return L

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

        if self.sep:
            sep_v = ' | '
            sep_h_int = '-+-'
            sep_h_line = '-'
        else:
            sep_v = '  '
            sep_h_int = '  '
            sep_h_line = ' '

        sep_h = sep_h_int.join([sep_h_line * self.cell_width] * self.config.col)

        if self.border:
            top = ('.-' + ('-' * len(sep_h)) + '-.')
            bottom = ("'-" + ('-' * len(sep_h)) + "-'")

            wrap = lambda lines: [top] + lines + [bottom]
            left, right = '| ', ' |'
            hr = ('|' + sep_h[0] + sep_h + sep_h[0] + '|')
        else:
            wrap = lambda lines: lines
            left = right = ''
            hr = sep_h

        matrix = to_matrix(self.colored, self.config.col, [])

        lines_of_rows = [
                [left + sep_v.join(slices) + right for slices in zip_longest(*row, fillvalue=' ' * self.cell_width)]
                for row in matrix
                ]
        framed_lines = wrap(sum(([hr] + lines for lines in lines_of_rows[1:]), lines_of_rows[0]))
        return framed_lines

    def render(self):
        return '\n'.join(self.framed)
