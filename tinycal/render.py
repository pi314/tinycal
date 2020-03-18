from unicodedata import east_asian_width

from .config import Color

border_template = {
        'template': [
            '┏━──────────────────────────┳┓',
            '┃        March 2020         ┃┃',
            '┃━━──┳─────────────────────━┃┃',
            '┃ WK ╋ Su Mo Tu We Th Fr Sa ┃┃',
            '┃ 10 ┃  1  2  3  4  5  6  7 ┃┃',
            '│ 11 │  8  9 10 11 12 13 14 ││',
            '│ 12 │ 15 16 17 18 19 20 21 ││',
            '│ 13 │ 22 23 24 25 26 27 28 ││',
            '│ 14 │ 29 30 31             ││',
            '┣━──────────────────────────╋┫',
            '┗━──────────────────────────┻┛',
            ],
        'ascii': [
            '.----------------------------.',
            '|           Title           ||',
            '| ------------------------- ||',
            '| WK | 日 月 火 水 木 金 土 ||',
            '| 10 |  1  2  3  4  5  6  7 ||',
            '| 11 |  8  9 10 11 12 13 14 ||',
            '| 12 | 15 16 17 18 19 20 21 ||',
            '| 13 | 22 23 24 25 26 27 28 ||',
            '| 14 | 29 30 31             ||',
            '|---------------------------+|',
            "'----------------------------'",
            ],
        'single': [
            '┌───────────────────────────┬┐',
            '│        March 2020         ││',
            '│────┬──────────────────────││',
            '│ WK ┼ Su Mo Tu We Th Fr Sa ││',
            '│ 10 │  1  2  3  4  5  6  7 ││',
            '│ 11 │  8  9 10 11 12 13 14 ││',
            '│ 12 │ 15 16 17 18 19 20 21 ││',
            '│ 13 │ 22 23 24 25 26 27 28 ││',
            '│ 14 │ 29 30 31             ││',
            '├───────────────────────────┼┤',
            '└───────────────────────────┴┘',
            ],
        'bold': [
            '┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳┓',
            '┃        March 2020         ┃┃',
            '┃━━━━┳━━━━━━━━━━━━━━━━━━━━━━┃┃',
            '┃ WK ╋ Su Mo Tu We Th Fr Sa ┃┃',
            '┃ 10 ┃  1  2  3  4  5  6  7 ┃┃',
            '┃ 11 ┃  8  9 10 11 12 13 14 ┃┃',
            '┃ 12 ┃ 15 16 17 18 19 20 21 ┃┃',
            '┃ 13 ┃ 22 23 24 25 26 27 28 ┃┃',
            '┃ 14 ┃ 29 30 31             ┃┃',
            '┣━━━━━━━━━━━━━━━━━━━━━━━━━━━╋┫',
            '┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┻┛',
            ],
        'double': [
            '╔═══════════════════════════╦╗',
            '║         2020              ║║',
            '║────┬──────────────────────║║',
            '║ WK ┼ Su Mo Tu We Th Fr Sa ║║',
            '║ 10 │  1  2  3  4  5  6  7 ║║',
            '║ 11 │  8  9 10 11 12 13 14 ║║',
            '║ 12 │ 15 16 17 18 19 20 21 ║║',
            '║ 13 │ 22 23 24 25 26 27 28 ║║',
            '║ 14 │ 29 30 31             ║║',
            '╠═══════════════════════════╬╣',
            '╚═══════════════════════════╩╝',
            ],
        }

def str_width(s):
    return sum(1 + (east_asian_width(c) in 'WF') for c in s)


class Cell:
    def __init__(self, config):
        self.config = config
        self.title = None
        self.weekday_title = ''
        self.wk_title = 'WK'
        self.lines = []
        self.assigned_height = 0

    def append(self, wk='', days=' ' * (7 * 2 + 6), month=''):
        self.lines.append((wk, days, month))

    @property
    def width(self):
        # 2 (cell padding)
        return self.internal_width + 2

    def padding(self, s):
        return ' ' + s + ' '

    @property
    def internal_width(self):
        # Cell width:
        # 7 (days per week) x 2 (spaces per day) +
        # 6 (paddings between days)
        # 5 (spaces for WK)
        mcw = self.month_col_width
        return (
                (7 * 2) +
                6 +
                (self.config.wk) * (3 + 2 * (self.config.border == 'full')) +
                mcw + (3 if mcw else 0)
                )

    @property
    def month_col_width(self):
        return max([str_width(line[2]) for line in self.lines])

    @property
    def height(self):
        # Only count dynamic part, i.e. no need to count title line
        return len(self.lines)

    @height.setter
    def height(self, val):
        self.assigned_height = val

    def __iter__(self):
        '''
        Each line of a Cell is contructed by the following parts:
            Title
            Cell internal border - title (if enabled)
            Weekdays
            Days
        '''

        if self.title is None:
            return

        bs = border_template[self.config.border_style]
        bc = self.config.color_border

        # Title
        pad_total = self.internal_width - str_width(self.title)
        pad = (pad_total // 2) * ' '
        self.title = pad + self.title + pad + (pad_total % 2) * ' '
        yield self.padding(self.config.color_title(self.title))

        mcw = self.month_col_width

        # Cell internal border - title (if enabled)
        if self.config.border == 'full':
            yield bc(bs[2][1] +
                    ('' if not self.config.wk else bs[2][2] * 3 + bs[2][5] + bs[2][2]) +
                    bs[2][2] * (7 * 2 + 6) +
                    ('' if not mcw else bs[2][2] + bs[2][5] + (mcw + 1) * bs[2][2]) +
                    bs[2][-3]
                    )

        def _render_wk(wk, wk_line):
            if not self.config.wk:
                return ''

            wk += ' '
            if self.config.border == 'full':
                wk += bc(bs[3 + int(not wk_line)][5]) + ' '

            return wk

        def _render_month(month):
            if mcw == 0:
                return ''
            else:
                rpad = mcw - str_width(month)
                return ' ' + bc(bs[4][5]) + ' ' + month + (rpad * ' ')

        # Weekdays
        yield self.padding(_render_wk(self.wk_title, True) + self.weekday_title + _render_month(''))

        # Days
        for wk, line, month in self.lines:
            yield self.padding(_render_wk(wk, False) + line + _render_month(month))

        for i in range(len(self.lines), self.assigned_height):
            yield self.padding(_render_wk('  ', False) + ' ' * (7 * 2 + 6))


class TinyCalRenderer:
    def __init__(self, config):
        self.config = config
        self.cells = []

    def append(self, cell):
        self.cells.append(cell)

    def render(self):
        try:
            from itertools import zip_longest
        except:
            from itertools import izip_longest as zip_longest

        # Select border style
        if self.config.border_style not in border_template:
            self.config.border_style = 'ascii'

        bs = border_template[self.config.border_style]
        bc = self.config.color_border

        # If month range < config.col, don't use empty cells to fill up
        effective_col = min(self.config.col, len(self.cells))

        def list_to_grid(seq, col):
            if len(seq) > col:
                return [seq[:col]] + list_to_grid(seq[col:], col)
            else:
                return [seq + [Cell(self.config)] * (col - len(seq))]

        grid = list_to_grid(self.cells, effective_col)

        cell_width = self.cells[0].width

        ret = ''

        # Top line
        if self.config.border != 'off':
            if self.config.border_weld:
                joiner = bs[0][-2]
            else:
                joiner = bs[0][-1] + bs[0][0]

            ret += bc(bs[0][0] + joiner.join([cell_width * bs[0][1]] * effective_col) + bs[0][-1]) + '\n'

        for row_idx, row in enumerate(grid):
            row_height = max(cell.height for cell in row)
            for cell in row:
                cell.height = row_height

            if row_idx > 0:
                # Inter-cell border
                if self.config.border == 'off':
                    ret += '\n'
                else:
                    if self.config.border_weld:
                        ret += bc(bs[-2][0] +
                                bs[-2][-2].join(((cell_width * bs[-2][1]) for cell in row)) +
                                bs[-2][-1]) + '\n'
                    else:
                        ret += bc(bs[-1][0] +
                                (bs[-1][-1] + bs[-1][0]).join(((cell_width * bs[-2][1]) for cell in row)) +
                                bs[-1][-1]) + '\n'
                        ret += bc(bs[0][0] +
                                (bs[0][-1] + bs[0][0]).join(((cell_width * bs[-2][1]) for cell in row)) +
                                bs[0][-1]) + '\n'

            # Days
            for line_nr, lines in enumerate(zip_longest(*row, fillvalue=' ' * cell_width)):
                border_idx = min([3, line_nr]) + 1
                if self.config.border != 'off':
                    if self.config.border_weld:
                        ret += (bc(bs[border_idx][0]) +
                                bc(bs[border_idx][-2]).join(lines) +
                                bc(bs[border_idx][-1]) + '\n')
                    else:
                        ret += (bc(bs[border_idx][0]) +
                                bc(bs[border_idx][-1] + bs[border_idx][0]).join(lines) +
                                bc(bs[border_idx][-1]) + '\n')

                else:
                    ret += ' '.join(lines) +'\n'

        # Bottom line
        if self.config.border != 'off':
            if self.config.border_weld:
                joiner = bs[-1][-2]
            else:
                joiner = bs[-1][-1] + bs[-1][0]

            ret += bc(bs[-1][0] + joiner.join([cell_width * bs[-1][1]] * effective_col) + bs[-1][-1]) + '\n'

        return ret.rstrip('\n')
