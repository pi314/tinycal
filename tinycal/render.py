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
'''

def str_width(s):
    return sum(1 + (east_asian_width(c) in 'WF') for c in s)


class Cell:
    def __init__(self, config):
        self.config = config
        self.title = None
        self._wk = []
        self._lines = []

    def append(self, month='', wk='', days=[]):
        assert isinstance(days, list) and len(days) == 7

        self._wk.append('{:>2}'.format(wk))
        self._lines.append(' '.join(days))

    @property
    def width(self):
        # Cell width:
        # 7 (days per week) x 2 (spaces per day) +
        # 6 (paddings between days)
        # 5 (spaces for WK)
        # 2 (cell padding)
        return 7 * 2 + 6 + (self.config.wk) * (5) + 2

    @property
    def height(self):
        return len(self._wk)

    def __iter__(self):
        '''
        Each line of a Cell is contructed by the following parts:
            Title
            Cell Internal border - title (if enabled)
            Weekdays
            Days
        '''

        if self.title is None:
            return

        # Title
        pad_total = self.width - str_width(self.title)
        pad = (pad_total // 2) * ' '
        self.title = pad + self.title + pad + (pad_total % 2) * ' '
        yield self.title

        # Cell Internal border - title (if enabled)
        yield ' ' + '-' * (self.width - 2) + ' '

        # Weekdays
        yield ' ' + ('WK | ' if self.config.wk else '') + ' '.join(self.weekday) + ' '

        # Days
        for wk, line in zip(self._wk, self._lines):
            yield ' ' + (wk + ' | ' if self.config.wk else '') + line + ' '


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

        ret = ''

        # Top line
        ret += '.' + '-'.join([self.cells[0].width * '-'] * effective_col) + '.' + '\n'

        for row_idx, row in enumerate(grid):
            if row_idx > 0:
                # Internal line
                ret += '|' + '+'.join(((self.cells[0].width * '-') for cell in row)) + '|' + '\n'

            # Days
            for lines in zip_longest(*row, fillvalue=' ' * self.cells[0].width):
                ret += '|' + '|'.join(lines) + '|\n'

        # Bottom line
        ret += "'" + '-'.join([self.cells[0].width * '-'] * effective_col) + "'" + '\n'

        return ret.rstrip('\n')
