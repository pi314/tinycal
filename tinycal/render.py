# -*- coding: utf-8 -*-

"""
Render calendar.
"""

from calendar import SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY

JAPANESE_WEEKDAY = ['月', '火', '水', '木', '金', '土', '日']
CHINESE_WEEKDAY = ['一', '二', '三', '四', '五', '六', '日']
BASE = max(SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY) + 1


class Month(object):
    def __init__(self, config, m):
        self.m = m
        self.config = config
        self.width = 7 * 2 + 6 + (3 if config.wk else 0)

        if m is None:
            self.weeks = []
        else:
            self.weeks = config.cal.monthdatescalendar(m.year, m.month)
            year_start = config.cal.monthdatescalendar(m.year, 1)[0][0]
            month_start = self.weeks[0][0]
            self.wk_start = int((month_start - year_start).days / 7)

    def render_title(self):
        if self.m is None:
            return ' ' * self.width

        title = self.m.strftime('%B') + ' %s' % self.m.year
        return self.config.color.title('{:^{}}'.format(title, self.width))

    def render_weekday(self):
        if self.m is None:
            return ' ' * self.width

        ret = self.config.color.wk('WK') if self.config.wk else ''

        ret += self.config.color.weekday[BASE].code
        ret += ' ' if self.config.wk else ''

        def render_single_weekday(d):
            c = self.config.color.weekday[d.weekday()]
            if self.config.lang == 'jp':
                ret = c(JAPANESE_WEEKDAY[d.weekday()])
            elif self.config.lang == 'zh':
                ret = c(CHINESE_WEEKDAY[d.weekday()])
            else:
                ret = c(d.strftime('%a')[:2])
            return ret + (self.config.color.weekday[BASE].code if c else '')

        ret += ''.join([' '.join(render_single_weekday(d) for d in self.weeks[0])])

        ret += '\033[0m' if self.config.color.weekday[BASE] else ''
        return ret

    def render_week(self, wk):
        if wk >= len(self.weeks):
            return ' ' * self.width

        ret = ''
        if self.config.wk:
            ret = ''.join([
                self.config.color.wk.code,
                str(self.wk_start + wk + 1).rjust(2),
                ('\033[0m' if self.config.color.wk else ''),
                ' '
            ])

        def render_single_day(d):
            if self.config.fill or d.month == self.m.month:
                c = ''

                if self.config.color:
                    if d == self.config.today:
                        c = self.config.color.today
                    elif d.month != self.m.month:
                        c = self.config.color.fill
                    else:
                        c = self.config.color.day[d.weekday()]

                return c(str(d.day).rjust(2))

            return '  '

        ret += ' '.join(render_single_day(d) for d in self.weeks[wk])
        return ret


class TinyCal:
    def __init__(self, config):
        self.config = config

    def cell(self, year, month): pass
    def render_cell(self): pass
    def render_table(self):
        try:
            from itertools import zip_longest
        except:
            from itertools import izip_longest as zip_longest

        config = self.config
        rows = [[Month(config, dt) for dt in row] for row in config.matrix]

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

        render_cell = lambda month: [month.render_title(), month.render_weekday()] \
                                    + [month.render_week(lineno) for lineno in range(len(month.weeks))]

        fillvalue = ' ' * rows[0][0].width

        lines_of_rows = []
        for row in rows:
            line_slices = zip_longest(*(render_cell(month) for month in row), fillvalue=fillvalue)
            lines = [left + sep_v.join(slices) + right for slices in line_slices]
            lines_of_rows.append(lines)
        lines = sum(([hr] + lines for lines in lines_of_rows[1:]), lines_of_rows[0])

        if config.border:
            lines = [top] + lines + [bottom]

        return lines

    def render(self):
        return '\n'.join(self.render_table())
