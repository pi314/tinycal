from unicodedata import east_asian_width

from .config import Color

border_style = {
        'ascii': [
            '.----------------------------.',
            '|           Title           ||',
            '| ------------------------- ||',
            '| WK | 日 月 火 水 木 金 土 ||',
            '| 10 |  1  2  3  4  5  6  7 ||',
            '| 11 |  8  9 10 11 12 13 14 ||',
            '| 12 | 15 16 17 18 19 20 21 ||',
            '| 13 | 22 23 24 25 26 27 28 ||',
            '| 14 | 29 30 31  1  2  3  4 ||',
            '|    |                      ||',
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
            '┃━━━━┳━━━━━━━━━━━━━━━━━━━━━━┃┫',
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
        self.weekday_text = ''
        self.wk_text = 'WK'
        self._wk = []
        self._lines = []
        self._height = 0
        self.border_style = None

    def append(self, month='', wk='', days=[]):
        assert isinstance(days, list) and len(days) == 7

        self._wk.append(wk)
        self._lines.append(' '.join(days))

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
        return 7 * 2 + 6 + (self.config.wk) * (3 + 2 * (self.config.border == 'full'))

    @property
    def height(self):
        # Only count dynamic part, i.e. no need to count title line
        return len(self._wk)

    @height.setter
    def height(self, val):
        self._height = val

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

        assert self.border_style
        bs = self.border_style

        # Title
        pad_total = self.internal_width - str_width(self.title)
        pad = (pad_total // 2) * ' '
        self.title = pad + self.title + pad + (pad_total % 2) * ' '
        yield self.padding(self.config.color_title(self.title))

        # Cell internal border - title (if enabled)
        if self.config.border == 'full':
            yield (bs[2][1] +
                    (bs[2][2] * 3 + bs[2][5] + bs[2][6] if self.config.wk else '') +
                    bs[2][6] * (7 * 2 + 6) +
                    bs[2][-3])

        def _render_wk(wk, wk_line):
            if not self.config.wk:
                return ''

            wk += ' '
            if self.config.border == 'full':
                wk += bs[3 + int(not wk_line)][5] + ' '

            return wk

        # Weekdays
        yield self.padding(_render_wk(self.wk_text, True) + self.weekday_text)

        # Days
        for wk, line in zip(self._wk, self._lines):
            yield self.padding(_render_wk(wk, False) + line)

        for i in range(len(self._wk), self._height):
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
        if self.config.border_style not in border_style:
            self.config.border_style = 'ascii'

        bs = border_style[self.config.border_style]

        # Apply border style to every cells
        for cell in self.cells:
            cell.border_style = bs

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

            ret += bs[0][0] + joiner.join([cell_width * bs[0][1]] * effective_col) + bs[0][-1] + '\n'

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
                        ret += (bs[-2][0] +
                                bs[-2][-2].join(((cell_width * bs[-2][1]) for cell in row)) +
                                bs[-2][-1] + '\n')
                    else:
                        ret += (bs[-1][0] +
                                (bs[-1][-1] + bs[-1][0]).join(((cell_width * bs[-2][1]) for cell in row)) +
                                bs[-1][-1] + '\n')
                        ret += (bs[0][0] +
                                (bs[0][-1] + bs[0][0]).join(((cell_width * bs[-2][1]) for cell in row)) +
                                bs[0][-1] + '\n')

            # Days
            for line_nr, lines in enumerate(zip_longest(*row, fillvalue=' ' * cell_width)):
                border_idx = min([3, line_nr]) + 1
                if self.config.border != 'off':
                    if self.config.border_weld:
                        ret += (bs[border_idx][0] +
                                bs[border_idx][-2].join(lines) +
                                bs[border_idx][-1] + '\n')
                    else:
                        ret += (bs[border_idx][0] +
                                (bs[border_idx][-1] + bs[border_idx][0]).join(lines) +
                                bs[border_idx][-1] + '\n')

                else:
                    ret += ' '.join(lines) +'\n'

        # Bottom line
        if self.config.border != 'off':
            if self.config.border_weld:
                joiner = bs[-1][-2]
            else:
                joiner = bs[-1][-1] + bs[-1][0]

            ret += bs[-1][0] + joiner.join([cell_width * bs[-1][1]] * effective_col) + bs[-1][-1] + '\n'

        return ret.rstrip('\n')
