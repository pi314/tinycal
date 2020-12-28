from itertools import zip_longest
from unicodedata import east_asian_width

from .color import Color
from .table_struct import Weekday


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

    template_example = '''
            ╔═──────────────────────────╦╗
            ║        March 2020         ║║
            ║══──╦──────────────────────║║
            │ WK ╬ Su Mo Tu We Th Fr Sa ││
            │ 10 ║  1  2  3  4  5  6  7 ││
            │ 11 │  8  9 10 11 12 13 14 ││
            │ 12 │ 15 16 17 18 19 20 21 ││
            │ 13 │ 22 23 24 25 26 27 28 ││
            │ 14 │ 29 30 31             ││
            ╠═──────────────────────────╬╣
            ╚═──────────────────────────╩╝
            '''

    template_ascii = """
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
            """


    template_single = '''
            ┌───────────────────────────┬┐
            │        March 2020         ││
            │────┬──────────────────────││
            │ WK ┼ Su Mo Tu We Th Fr Sa ││
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
            ┃ WK ╋ Su Mo Tu We Th Fr Sa ┃┃
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
            ║ WK ┼ Su Mo Tu We Th Fr Sa ║║
            ║ 10 │  1  2  3  4  5  6  7 ║║
            ║ 11 │  8  9 10 11 12 13 14 ║║
            ║ 12 │ 15 16 17 18 19 20 21 ║║
            ║ 13 │ 22 23 24 25 26 27 28 ║║
            ║ 14 │ 29 30 31             ║║
            ╠═══════════════════════════╬╣
            ╚═══════════════════════════╩╝
            '''

    template_test = '''
            ╔═══════════════════════════╤╗
            ║         2020              │║
            ║────┬──────────────────────│║
            ║ WK ┼ Su Mo Tu We Th Fr Sa │║
            ║ 10 │  1  2  3  4  5  6  7 │║
            ║ 11 │  8  9 10 11 12 13 14 │║
            ║ 12 │ 15 16 17 18 19 20 21 │║
            ║ 13 │ 22 23 24 25 26 27 28 │║
            ║ 14 │ 29 30 31             │║
            ╟───────────────────────────┼╢
            ╚═══════════════════════════╧╝
            '''


    def __init__(self, style, richness, weld, wk, color):
        self.style = style
        self.richness = richness
        self.weld = weld
        self.wk = wk
        self.color = color

        try:
            template = getattr(BorderTemplate, 'template_' + self.style)
        except AttributeError:
            template = getattr(BorderTemplate, 'template_example')

        self.template = list(map(str.strip, template.strip().split('\n')))
        self.cell_width = cell_width(self.richness, self.wk)

    @property
    def title_sep(self):
        if self.richness != 'full':
            return None

        t = self.template
        ret = t[2][1]
        if self.wk:
            ret += (t[2][2] * 3) + t[2][5] + t[2][2]

        ret += (t[2][2] * 20) + t[2][1]
        return self.color(ret)

    def wk_sep_line(self, idx):
        return self.color(self.template[(3 if idx == 0 else 4)][5])

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
                (t[0][1] * cw,) if self.weld else (t[-1][1] * cw, t[0][1] * cw),
                t[-1][1] * cw,
                t[1][0],
                t[1][-2] if self.weld else (t[1][-1] + t[1][0]),
                t[1][-1],
                ][number]

        if isinstance(ret, tuple):
            return tuple(map(self.color, ret))
        return self.color(ret)

    def __getitem__(self, idx):
        return self.template[idx]


class TinyCalTableTextNode:
    def __init__(self, text):
        self.color = Color('')
        self.text = str(text)

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return self.color(self.text)


def str_width(s):
    return sum(1 + (east_asian_width(c) in 'WF') for c in s)


def mjust(string, width):
    a = str_width(string)
    left = (width - a) // 2
    right = width - a - left
    return (left * ' ') + string + (right * ' ')


def rjust(string, width):
    return ' ' * (width - str_width(string)) + string


def cell_width(border_richness, wk):
    return (2 * 7 + 8) + wk * (3 + 2 * (border_richness == 'full'))


def render_classic(conf, tr, cal_table, drange, today):
    cw = cell_width(conf.border_richness, conf.wk)

    # Squash conf.color_default into a single Color object
    conf.color_default = sum(conf.color_default[1:], conf.color_default[0])

    # Squash color configs that won't change anymore
    conf.color_title = conf.color_default + conf.color_title

    # bt = BorderTemplate(conf.border_style, conf.border_richness, conf.border_weld, conf.wk, conf.color_border)
    bt = BorderTemplate('example', conf.border_richness, conf.border_weld, conf.wk, conf.color_default + conf.color_border)

    '''
    Expand TinyCalTable content into colored strings and shape them into rectangle
    '''
    output_table = []
    for cal_row in cal_table.rows:
        output_row = []

        row_height = 0
        for cal_cell in cal_row.cells:
            if not cal_cell:
                output_row.append([])
                continue

            # Render title
            output_cell = [' ' + conf.color_title(mjust(cal_cell.title, cw-2)) + ' ']

            if conf.border_richness == 'full':
                output_cell.append(bt.title_sep)

            for idx, cal_week in enumerate(cal_cell.weeks):
                week_buf = ' '
                if conf.wk:
                    # Render WK
                    wk_color = conf.color_default + conf.color_wk
                    if today in cal_week.days:
                        wk_color += conf.color_today_wk

                    week_buf += wk_color(rjust(str(cal_week.wk), 2)) + ' '
                    week_buf += bt.wk_sep_line(idx) + ' '

                for node in cal_week.days:
                    if isinstance(node, Weekday):
                        # Render weekdays
                        wkd = int(node)
                        wkd_color = conf.color_default + conf.color_weekday
                        wkd_color += getattr(conf, 'color_weekday_' + tr.weekday_meta[wkd])
                        week_buf += wkd_color(tr.weekday[wkd]) + ' '

                    else:
                        # Render dates
                        day_color = conf.color_default
                        day_color += getattr(conf, 'color_' + tr.weekday_meta[node.weekday()])
                        if node == today:
                            day_color += conf.color_today

                        week_buf += day_color(rjust(str(node.day), 2)) + ' '

                output_cell.append(week_buf)

            row_height = max(row_height, len(output_cell))

            output_row.append(output_cell)

        # Make up cells that are too short
        for cell in output_row:
            lc = len(cell)
            for i in range(lc, row_height):
                if lc:
                    cell.append((('    ' + bt.wk_sep_line(1)) * conf.wk) + (' ' * (cw - 5)))
                else:
                    cell.append(' ' * cw)

        output_table.append(output_row)

    '''
    Render the result
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
