# -*- coding: utf-8 -*-

"""
Render calendar.
"""

from calendar import SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY

JAPANESE_WEEKDAY = ['月', '火', '水', '木', '金', '土', '日']
CHINESE_WEEKDAY = ['一', '二', '三', '四', '五', '六', '日']
BASE = max(SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY) + 1


def color(s, c):
    return c + s + ('\033[0m' if c else '')


def uncolor(color):
    return '\033[0m' if color else ''


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

        ret += self.config.color.weekday[BASE]
        ret += ' ' if self.config.wk else ''

        def render_single_weekday(d):
            c = self.config.color.weekday[d.weekday()]
            if self.config.lang == 'jp':
                ret = color(JAPANESE_WEEKDAY[d.weekday()], c)
            elif self.config.lang == 'zh':
                ret = color(CHINESE_WEEKDAY[d.weekday()], c)
            else:
                ret = color(d.strftime('%a')[:2], c)
            return ret + (self.config.color.weekday[BASE] if c else '')

        ret += ''.join([
            ' '.join(
                render_single_weekday(d)
                for d in self.weeks[0]
            ),
        ])

        ret += '\033[0m' if self.config.color.weekday[BASE] else ''
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

        def render_single_day(d):
            if self.config.fill or d.month == self.month:
                c = ''

                if self.config.color:
                    if d == self.config.today:
                        c = self.config.color.today
                    elif d.month != self.month:
                        c = self.config.color.fill
                    else:
                        c = self.config.color.day[d.weekday()]

                return color(str(d.day).rjust(2), c)

            return '  '

        ret += ' '.join(render_single_day(d) for d in self.weeks[wk])
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
