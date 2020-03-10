from unicodedata import east_asian_width

from .config import Color

'''
    ┌───────────────────────────┬───────────────────────────┐
    │        March 2020         │         April 2020        │
    ├────┬──────────────────────┼────┬──────────────────────┤
    ├ WK ┼ Su Mo Tu We Th Fr Sa ┼ WK ┼ Su Mo Tu We Th Fr Sa ┤
    │ 10 │  1  2  3  4  5  6  7 │ 14 │           1  2  3  4 │
    │ 11 │  8  9 10 11 12 13 14 │ 15 │  5  6  7  8  9 10 11 │
    │ 12 │ 15 16 17 18 19 20 21 │ 16 │ 12 13 14 15 16 17 18 │
    │ 13 │ 22 23 24 25 26 27 28 │ 17 │ 19 20 21 22 23 24 25 │
    │ 14 │ 29 30 31             │ 18 │ 26 27 28 29 30       │
    └────┴──────────────────────┴────┴──────────────────────┘
    ┌───────────────────────────────┐
    │             2020              │
    ├───┬────┬──────────────────────┤
    │   ├ WK ┼ Su Mo Tu We Th Fr Sa ┤
    │Mar│ 10 │  1  2  3  4  5  6  7 │
    │   │ 11 │  8  9 10 11 12 13 14 │
    │   │ 12 │ 15 16 17 18 19 20 21 │
    │   │ 13 │ 22 23 24 25 26 27 28 │
    │Apr│ 14 │ 29 30 31  1  2  3  4 │
    │   │ 15 │  5  6  7  8  9 10 11 │
    │   │ 16 │ 12 13 14 15 16 17 18 │
    │   │ 17 │ 19 20 21 22 23 24 25 │
    │   │ 18 │ 26 27 28 29 30       │
    └───┴────┴──────────────────────┘
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃        March 2020         ┃         April 2020        ┃
    ┣━━━━┳━━━━━━━━━━━━━━━━━━━━━━╋━━━━┳━━━━━━━━━━━━━━━━━━━━━━┫
    ┣ WK ╋ Su Mo Tu We Th Fr Sa ╋ WK ╋ Su Mo Tu We Th Fr Sa ┫
    ┃ 10 ┃  1  2  3  4  5  6  7 ┃ 14 ┃           1  2  3  4 ┃
    ┃ 11 ┃  8  9 10 11 12 13 14 ┃ 15 ┃  5  6  7  8  9 10 11 ┃
    ┃ 12 ┃ 15 16 17 18 19 20 21 ┃ 16 ┃ 12 13 14 15 16 17 18 ┃
    ┃ 13 ┃ 22 23 24 25 26 27 28 ┃ 17 ┃ 19 20 21 22 23 24 25 ┃
    ┃ 14 ┃ 29 30 31             ┃ 18 ┃ 26 27 28 29 30       ┃
    ┗━━━━┻━━━━━━━━━━━━━━━━━━━━━━┻━━━━┻━━━━━━━━━━━━━━━━━━━━━━┛
    ╔═══════════════════════════════╗
    ║             2020              ║
    ╟───┬────┬──────────────────────╢
    ║   ├ WK ┼ Su Mo Tu We Th Fr Sa ╢
    ║Mar│ 10 │  1  2  3  4  5  6  7 ║
    ║   │ 11 │  8  9 10 11 12 13 14 ║
    ║   │ 12 │ 15 16 17 18 19 20 21 ║
    ║   │ 13 │ 22 23 24 25 26 27 28 ║
    ║Apr│ 14 │ 29 30 31  1  2  3  4 ║
    ║   │ 15 │  5  6  7  8  9 10 11 ║
    ║   │ 16 │ 12 13 14 15 16 17 18 ║
    ║   │ 17 │ 19 20 21 22 23 24 25 ║
    ║   │ 18 │ 26 27 28 29 30       ║
    ╚═══╧════╧══════════════════════╝
'''

def str_width(s):
    return sum(1 + (east_asian_width(c) in 'WF') for c in s)


class Cell:
    def __init__(self, config):
        self.config = config
        self.title = None
        self.weekday_line = ''
        self.wk = 'WK'
        self._wk = []
        self._lines = []
        self._height = 0

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

        # Title
        pad_total = self.internal_width - str_width(self.title)
        pad = (pad_total // 2) * ' '
        self.title = pad + self.title + pad + (pad_total % 2) * ' '
        yield self.padding(self.config.color_title(self.title))

        # Cell internal border - title (if enabled)
        if self.config.border == 'full':
            yield self.padding('-' * (self.width - 2))

        def _render_wk(wk):
            if not self.config.wk:
                return ''

            wk += ' '
            if self.config.border == 'full':
                wk += '| '

            return wk

        # Weekdays
        yield self.padding(_render_wk(self.wk) + self.weekday_line)

        # Days
        for wk, line in zip(self._wk, self._lines):
            yield self.padding(_render_wk(wk) + line)

        for i in range(len(self._wk), self._height):
            yield self.padding(_render_wk('  ') + ' ' * (7 * 2 + 6))


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
            ret += '.' + '-'.join([cell_width * '-'] * effective_col) + '.' + '\n'

        for row_idx, row in enumerate(grid):
            row_height = max(cell.height for cell in row)
            for cell in row:
                cell.height = row_height

            if row_idx > 0 and self.config.border != 'off':
                # Inter-cell border
                if self.config.border != 'off':
                    ret += '|' + '+'.join(((cell_width * '-') for cell in row)) + '|' + '\n'

            # Days
            for lines in zip_longest(*row, fillvalue=' ' * cell_width):
                if self.config.border != 'off':
                    ret += '|' + '|'.join(lines) + '|\n'

                else:
                    ret += ' '.join(lines) +'\n'

        # Bottom line
        if self.config.border != 'off':
            ret += "'" + '-'.join([cell_width * '-'] * effective_col) + "'" + '\n'

        return ret.rstrip('\n')
