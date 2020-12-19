class TinyCalTableTextNode:
    def __init__(self):
        self.color = Color('')
        self.text = ''

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return self.color(self.text)


class TinyCalTableTextRow:
    def __init__(self, wk):
        self.wk = wk
        self.nodes = []

    def append(self, node):
        self.nodes.append(node)

    def __iter__(self):
        for node in self.nodes:
            yield node


class TinyCalTableCell:
    def __init__(self):
        self.title = ''
        self.rows = []

    @property
    def height(self):
        return len(self.rows)

    def append(self, row):
        self.rows.append(row)

    def __iter__(self):
        for row in self.rows:
            yield row


class TinyCalTableRow:
    def __init__(self):
        self.cells = []

    def __len__(self):
        return len(self.cells)

    @property
    def height(self):
        return max(cell.height for cell in self.cells)


class TinyCalTable:
    def __init__(self):
        self.rows = []

    def append(self, row):
        self.rows.append(row)
