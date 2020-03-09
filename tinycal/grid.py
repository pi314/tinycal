from unicodedata import east_asian_width

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
    def __init__(self, title):
        assert isinstance(title, str)

        self.title = title
        self._month = []
        self._wk = []
        self._lines = []

    def append(self, month='', wk='', days=[]):
        assert isinstance(days, list) and len(days) == 7

        self._month.append(str(month))
        self._wk.append('{:>2}'.format(wk))
        self._lines.append(' '.join(days))

    @property
    def height(self):
        return len(self._lines)

    def wk(self, idx):
        try:
            return self._wk[idx]
        except IndexError:
            return '  '

    def line(self, idx):
        try:
            return self._lines[idx]
        except IndexError:
            return ' ' * (7 * 2 + 6)


class Grid:
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

        # Cell width:
        # 7 (days per week) x 2 (spaces per day) +
        # 6 (paddings between days)
        # 2 (spaces for WK)
        cell_width = 7 * 2 + 6 + (self.config.wk) * (3)

        def list_to_grid(seq, col):
            if len(seq) > col:
                return [seq[:col]] + list_to_grid(seq[col:], col)
            else:
                return [seq + [None] * (col - len(seq))]

        def render_title(title):
            pad_total = cell_width - str_width(title)
            pad_l = (pad_total // 2) * ' '
            pad_r = (pad_total // 2 + (pad_total % 2)) * ' '
            return self.config.color_title('{}{}{}'.format(pad_l, title, pad_r))

        grid = list_to_grid(self.cells, effective_col)

        ret = ''

        # Top line
        ret += '.-' + '---'.join(((cell_width * '-') for cell in grid[0])) + '-.' + '\n'

        for row_idx, row in enumerate(grid):
            '''
            For each row (month list), construct the output line by line.
            Each line is contructed by the following parts:
                Title
                Cell Internal line (if enabled)
                Weekdays
                Days
            '''

            if row_idx > 0:
                # Internal line
                ret += '|-' + '-|-'.join(((cell_width * '-') for cell in row)) + '-|' + '\n'

            # Title
            ret += '| ' + ' | '.join([render_title(cell.title) for cell in row]) + ' |' + '\n'

            # Cell Internal line
            # Weekdays

            # Days
            row_height = max(cell.height for cell in row)
            for line in range(row_height):
                ret += '| '
                for col, cell in enumerate(row):

                    if col == 0:
                        pass
                    else:
                        ret += ' | '

                    if self.config.wk:
                        ret += cell.wk(line) + ' '

                    ret += cell.line(line)

                ret += ' |\n'

        # Bottom line
        ret += "'-" + '---'.join(((cell_width * '-') for cell in grid[0])) + "-'" + '\n'

        return ret.rstrip('\n')
