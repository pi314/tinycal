from datetime import timedelta
from itertools import zip_longest
from unicodedata import east_asian_width

from .color import Color
from .table_struct import Weekday, Date


def str_width(s):
    return sum(1 + (east_asian_width(c) in 'WF') for c in s)


def mjust(string, width):
    a = str_width(string)
    left = (width - a) // 2
    right = width - a - left
    return (left * ' ') + string + (right * ' ')


def rjust(string, width):
    return ' ' * (width - str_width(string)) + string


class BorderTemplate:
    '''
    Table corners numbering:
        1      2   3
        ╔──────╦───╗
        │ cell │   │
       4╠──────╬───╣6
        │     5│   │
        ╚──────╩───╝
        7      8   9
        if weld is True, 4 will be (7, 1)

    Table borders numbering:
        4      5   6
    1-->┌══════┬───┐
        ║ cell ║   ║
    2-->├══════┼───┤
        │      │   │
    3-->└══════┴───┘
        if weld is True, 2 will be (1, 3)
    '''

    '''
    Currently the table border is cell-content-independent
    It cannot connect into the cell
    '''

    #TODO: how to define a template, how to parse a template

    template_example = '''
            ╔═────────────────────────────╦╗
            ║         March 2020          ║║
            ║══──╦────────────────────────║║
            │ WK ║  Su Mo Tu We Th Fr Sa  ││
            │ 10 │╔  1  2  3  4  5  6  7 ╗││
            │ 11 │║  8  9 10 11 12 13 14 ║││
            │ 12 ││ 15 16 17 18 19 20 21 │││
            │ 13 ││ 22 23 24 25 26 27 28 ╝││
            │ 14 │╚ 29 30 31              ││
            ╠═────────────────────────────╬╣
            ╚═────────────────────────────╩╝
            '''

    template_ascii = '''
            .----------------------------.
            |           Title           ||
            | ------------------------- ||
            | WK | 日 月 火 水 木 金 土 ||
            | 10 |  1  2  3  4  5  6  7 ||
            | 11 |  8  9 10 11 12 13 14 ||
            | 12 | 15 16 17 18 19 20 21 ||
            | 13 | 22 23 24 25 26 27 28 ||
            | 14 | 29 30 31             ||
            |---------------------------+|
            '----------------------------'
            '''

    template_single = '''
            ┌───────────────────────────┬┐
            │        March 2020         ││
            │────┬──────────────────────││
            │ WK │ Su Mo Tu We Th Fr Sa ││
            │ 10 │  1  2  3  4  5  6  7 ││
            │ 11 │  8  9 10 11 12 13 14 ││
            │ 12 │ 15 16 17 18 19 20 21 ││
            │ 13 │ 22 23 24 25 26 27 28 ││
            │ 14 │ 29 30 31             ││
            ├───────────────────────────┼┤
            └───────────────────────────┴┘
            '''

    template_bold = '''
            ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳┓
            ┃        March 2020         ┃┃
            ┃━━━━┳━━━━━━━━━━━━━━━━━━━━━━┃┃
            ┃ WK ┃ Su Mo Tu We Th Fr Sa ┃┃
            ┃ 10 ┃  1  2  3  4  5  6  7 ┃┃
            ┃ 11 ┃  8  9 10 11 12 13 14 ┃┃
            ┃ 12 ┃ 15 16 17 18 19 20 21 ┃┃
            ┃ 13 ┃ 22 23 24 25 26 27 28 ┃┃
            ┃ 14 ┃ 29 30 31             ┃┃
            ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━╋┫
            ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┻┛
            '''

    template_double = '''
            ╔═══════════════════════════╦╗
            ║         2020              ║║
            ║────┬──────────────────────║║
            ║ WK │ Su Mo Tu We Th Fr Sa ║║
            ║ 10 │  1  2  3  4  5  6  7 ║║
            ║ 11 │  8  9 10 11 12 13 14 ║║
            ║ 12 │ 15 16 17 18 19 20 21 ║║
            ║ 13 │ 22 23 24 25 26 27 28 ║║
            ║ 14 │ 29 30 31             ║║
            ╠═══════════════════════════╬╣
            ╚═══════════════════════════╩╝
            '''

    template_frame = '''
            ╔═══════════════════════════╤╗
            ║         2020              │║
            ║────┬──────────────────────│║
            ║ WK │ Su Mo Tu We Th Fr Sa │║
            ║ 10 │  1  2  3  4  5  6  7 │║
            ║ 11 │  8  9 10 11 12 13 14 │║
            ║ 12 │ 15 16 17 18 19 20 21 │║
            ║ 13 │ 22 23 24 25 26 27 28 │║
            ║ 14 │ 29 30 31             │║
            ╟───────────────────────────┼╢
            ╚═══════════════════════════╧╝
            '''

    def __init__(self, conf):
        self.style = conf.border_style
        self.richness = conf.border_richness
        self.weld = conf.border_weld
        self.wk = conf.wk
        self.color = conf.color_default + conf.color_border
        self.color_month_hint_range = self.color + conf.color_month_hint_range

        try:
            template = getattr(self.__class__, 'template_' + self.style)
        except AttributeError:
            template = getattr(self.__class__, 'template_example')

        self.template = list(map(str.strip, template.strip().split('\n')))

        self.month_hint_range_enable = False
        self.month_hint_sep_enable = False
        self.month_hint_text_enable = False

        if conf.mode == 'week' and conf.month_hint_range:
            # Parse month range indicator from template
            self._month_hint_range_ind = self._extract_month_hint_range_ind()

            if self._month_hint_range_ind:
                self.month_hint_range_enable = True

        if conf.mode == 'week':
            self.month_hint_sep_enable = (conf.month_hint_sep and conf.month_hint_text)
            self.month_hint_text_enable = conf.month_hint_text

    def _extract_month_hint_range_ind(self):
        t = self.template[4:-2]

        # Check template width, if not wide enough, it meas no month hint range int
        # I'm hardcoding it here as the template format may change
        if not all(map(lambda x: len(x) == 32, t)):
            return None

        l = ''.join(filter(lambda x: x != ' ', (i[6] for i in t)))
        r = ''.join(filter(lambda x: x != ' ', (i[-3] for i in t)))

        if len(l) < 3 or len(r) < 3:
            return None

        l  = l[0] + l[1] + l[-1]
        r  = r[0] + r[1] + r[-1]
        return (l, r)

    @property
    def cell_width(self):
        return sum((
                2 * 7 + 8,
                self.wk * (3 + 2 * (self.richness == 'full')),
                2 * self.month_hint_range_enable,
                1 * self.month_hint_sep_enable,
                9 * self.month_hint_text_enable,
                ))

    @property
    def month_hint_sep(self):
        if not self.month_hint_sep_enable:
            return ''

        return self.wk_sep

    def month_hint_range_ind(self, left_right, idx):
        if not self.month_hint_range_enable:
            return ''

        if idx == -1:
            return ' '

        return self.color_month_hint_range(self._month_hint_range_ind[left_right][idx])

    @property
    def title_sep(self):
        if self.richness != 'full':
            return None

        t = self.template
        ret = ''
        if self.wk:
            ret += (t[2][2] * 4) + t[2][5]

        ret += self.month_hint_range_enable * t[2][2]
        ret += (7 * 2 + 8) * t[2][2]
        ret += self.month_hint_range_enable * t[2][2]
        ret += self.month_hint_sep_enable * t[2][5]
        ret += self.month_hint_text_enable * 9 * t[2][2]

        return self.color(t[2][1] + ret[1:-1] + t[2][1])

    @property
    def wk_sep(self):
        return self.color(self.template[3][5])

    def table_corner(self, number):
        t = self.template
        tc = self.table_corner
        ret = [
                None,
                t[0][0],
                t[0][-2] if self.weld else (t[0][-1] + t[0][0]),
                t[0][-1],
                (t[-2][0],) if self.weld else (t[-1][0], t[0][0]),
                (t[-2][-2],) if self.weld else (t[-1][-1] + t[-1][0], t[0][-1] + t[0][0]),
                (t[-2][-1],) if self.weld else (t[-1][-1], t[0][-1]),
                t[-1][0],
                t[-1][-2] if self.weld else (t[-1][-1] + t[-1][0]),
                t[-1][-1],
                ][number]

        if isinstance(ret, tuple):
            return tuple(map(self.color, ret))

        return self.color(ret)

    def table_border(self, number):
        t = self.template
        tb = self.table_border
        cw = self.cell_width
        ret = [
                None,
                t[0][1] * cw,
                (t[-2][1] * cw,) if self.weld else (t[-1][1] * cw, t[0][1] * cw),
                t[-1][1] * cw,
                t[1][0],
                t[1][-2] if self.weld else (t[1][-1] + t[1][0]),
                t[1][-1],
                ][number]

        if isinstance(ret, tuple):
            return tuple(map(self.color, ret))

        return self.color(ret)


def render_classic(conf, tr, date_marks, today, cal_table):
    # Squash conf.color_default into a single Color object
    conf.color_default = conf.color_default[0] + conf.color_default[1:]

    # Squash color configs that won't change anymore
    conf.color_title = conf.color_default + conf.color_title
    conf.color_fill = conf.color_fill[0] + conf.color_fill[1:]
    conf.color_month_hint_text = conf.color_default + conf.color_month_hint_text

    conf.border_style = 'example'
    bt = BorderTemplate(conf)
    cw = bt.cell_width

    output_table = render_classic_table_cells(conf, tr, date_marks, today, bt, cw, cal_table)
    render_classic_table_border(bt, output_table)


def render_classic_table_cells(conf, tr, date_marks, today, bt, cw, cal_table):
    '''
    Expand TinyCalTable content into colored strings and shape them into rectangle
    '''
    output_table = []
    for cal_row in cal_table.rows:
        output_row = []

        for cal_cell in cal_row.cells:
            output_cell = render_classic_cell(conf, tr, date_marks, today, bt, cw, cal_cell)
            output_row.append(output_cell)

        row_height = max(map(len, output_row))

        # Make up cells that are too short
        # zip() will be used on cells later, which makes shortest one decides the height
        for cell in output_row:
            lc = len(cell)
            for i in range(lc, row_height):
                # For non-empty cells, a wk_sep is necessary
                if lc and conf.border_richness == 'full' and conf.wk:
                    cell.append(('    ' + bt.wk_sep) + (' ' * (cw - 5)))
                else:
                    cell.append(' ' * cw)

        output_table.append(output_row)

    return output_table


def render_classic_cell(conf, tr, date_marks, today, bt, cw, cal_cell):
    if not cal_cell:
        return []

    # Render title
    output_cell = [' ' + conf.color_title(mjust(cal_cell.title, cw - 2)) + ' ']

    if conf.border_richness == 'full':
        output_cell.append(bt.title_sep)

    # Render week
    for cal_week in cal_cell.weeks:
        output_week = render_classic_week(conf, tr, date_marks, today, bt, cw, cal_week)
        output_cell.append(output_week)

    return output_cell


def render_classic_week(conf, tr, date_marks, today, bt, cw, cal_week):
    output_week = ''

    # Render WK
    if conf.wk:
        wk_color = conf.color_default + conf.color_wk
        if today in cal_week.days:
            wk_color += conf.color_today_wk

        output_week += ' ' + wk_color(rjust(str(cal_week.wk), 2))
        if conf.border_richness == 'full':
            output_week += ' ' + bt.wk_sep

    # Prepare month hint
    month_hint_range_ind = []
    for left_right, d in zip((0, 1), (cal_week.days[0], cal_week.days[6])):
        if isinstance(d, Weekday):
            month_hint_range_ind.append(bt.month_hint_range_ind(left_right, -1))
        elif d.month != (d - timedelta(days=7)).month:
            month_hint_range_ind.append(bt.month_hint_range_ind(left_right, 0))
        elif d.month != (d + timedelta(days=7)).month:
            month_hint_range_ind.append(bt.month_hint_range_ind(left_right, 2))
        else:
            month_hint_range_ind.append(bt.month_hint_range_ind(left_right, 1))

    # Render month hint (left)
    output_week += month_hint_range_ind[0]

    def get_padding_color(d):
        padding_color = conf.color_default
        for dm in date_marks:
            if d.is_fill or (d - timedelta(days=1)).is_fill:
                pass
            elif d in dm and (d - timedelta(days=1)) in dm:
                padding_color += dm.color

        return padding_color

    # Render first padding
    if isinstance(cal_week.days[0], Date):
        output_week += get_padding_color(cal_week.days[0])(' ')
    else:
        output_week += ' '

    # Render days
    for node in cal_week.days:
        # Render weekdays
        if isinstance(node, Weekday):
            wkd = int(node)
            wkd_color = conf.color_default
            wkd_color += conf.color_weekday
            wkd_color += getattr(conf, 'color_weekday_' + tr.weekday_meta[wkd])
            output_week += wkd_color(tr.weekday[wkd]) + ' '
            continue

        # Render dates
        if node.is_fill:
            if not conf.fill:
                ds = '  ' + ' '
            else:
                ds = conf.color_fill(rjust(str(node.day), 2)) + ' '

        else:
            day_color = conf.color_default
            day_color += getattr(conf, 'color_' + tr.weekday_meta[node.weekday()])
            day_color += [dm.color for dm in date_marks if node in dm]

            if node == today:
                day_color += conf.color_today

            ds = day_color(rjust(str(node.day), 2)) + get_padding_color(node)(' ')

        output_week += ds

    # Render month hint (right)
    output_week += month_hint_range_ind[1]

    # Render month hint (text)
    if conf.mode == 'week':
        output_week += bt.month_hint_sep
        if conf.month_hint_text:
            output_week += ' ' + conf.color_month_hint_text(cal_week.hint.rjust(7)) + ' '

    return output_week


def render_classic_table_border(bt, output_table):
    '''
    Surround rendered cell content with table borders
    '''
    for row_idx, output_row in enumerate(output_table):
        if row_idx == 0:
            print(
                    bt.table_corner(1) +
                    bt.table_corner(2).join((bt.table_border(1),) * len(output_row)) +
                    bt.table_corner(3)
                    )

        for line_idx, line in enumerate(zip(*output_row)):
            print(bt.table_border(4) + bt.table_border(5).join(line) + bt.table_border(6))

        if row_idx == len(output_table) - 1:
            print(
                    bt.table_corner(7) +
                    bt.table_corner(8).join((bt.table_border(3),) * len(output_row)) +
                    bt.table_corner(9)
                    )
        else:
            for comp in zip(bt.table_corner(4), bt.table_corner(5), bt.table_corner(6), bt.table_border(2)):
                print(comp[0] + comp[1].join((comp[3],) * len(output_row)) + comp[2])
