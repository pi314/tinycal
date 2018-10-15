# -*- coding: utf-8 -*-

"""
Render calendar.
"""

from calendar import (
        Calendar,
        SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY,
        )

JAPANESE_WEEKDAY = ['月', '火', '水', '木', '金', '土', '日']
CHINESE_WEEKDAY = ['一', '二', '三', '四', '五', '六', '日']
BASE = max(SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY) + 1


def color(s, c):
    return c + s + ('\033[0m' if c else '')


class Month(object):
    def __init__(self, cal, m):
        if m is None:
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
                ('\033[0m' if self.config.color.wk else ''),
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


def render(config):
    cal = TinyCalendar(config)
    rows = [[Month(cal, m) for m in row] for row in config.matrix]

    for row in rows:
        for m in row:
            m.set_render_config(config)

    if config.sep:
        sep_v = ' | '
        sep_h_int = '-+-'
        sep_h_line = '-'
    else:
        sep_v = '  '
        sep_h_int = '  '
        sep_h_line = ' '
    sep_h = sep_h_int.join(sep_h_line * m.width for m in rows[0])

    if config.border:
        top = ('.-' + ('-' * len(sep_h)) + '-.')
        bottom = ("'-" + ('-' * len(sep_h)) + "-'")
        hr = ('|' + sep_h[0] + sep_h + sep_h[0] + '|')
        left, right = '| ', ' |'
    else:
        left = right = ''
        hr = sep_h

    output_lines = []
    for row in rows:
        title = sep_v.join(m.render_title() for m in row)
        th = sep_v.join(m.render_weekday() for m in row)
        height = max(len(tm.weeks) for tm in row)
        for line in [title, th] + [sep_v.join(m.render_week(wk) for m in row) for wk in range(height)]:
            output_lines.append(left + line + right)
        output_lines.append(hr)
    output_lines.pop()

    if config.border:
        output_lines.insert(0, top)
        output_lines.append(bottom)

    return output_lines


class TinyCalendar(Calendar):
    def __init__(self, config):
        firstweekday = MONDAY if config.start_monday else SUNDAY
        super(TinyCalendar, self).__init__(firstweekday)
