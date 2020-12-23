from datetime import timedelta


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
    def __init__(self, title):
        self.title = title
        self.rows = []

    def __len__(self):
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

    def append(self, row):
        self.cells.append(row)

    def __iter__(self):
        for cell in self.cells:
            yield cell

    @property
    def height(self):
        return max(len(cell) for cell in self.cells)


class TinyCalTable:
    def __init__(self):
        self.rows = []

    def append(self, row):
        self.rows.append(row)

    def __iter__(self):
        for row in self.rows:
            yield row


def cal_week_num(cal, date):
    return ((date - cal.monthdatescalendar(date.year, 1)[0][0]).days // 7) + 1


def construct_table(conf, tr, cal, drange):
    # Construct output table structure
    cal_table = TinyCalTable()

    if not conf.cont:
        print('start =', drange[0].to_date())
        print('end =  ', drange[1].to_date())
        print()

        for idx, umn in enumerate(range(drange[0].umn, drange[1].umn + 1)):
            if idx % conf.col == 0:
                cal_row = TinyCalTableRow()
                cal_table.append(cal_row)

            year = umn // 12
            month = (umn % 12) + 1

            cal_cell = TinyCalTableCell('{m} {y}'.format(m=tr.month(month), y=year))

            # Put Weekday header
            text_row = TinyCalTableTextRow(tr.weekday(-1))
            text_row.append(' ')
            for wkd in cal.iterweekdays():
                text_row.append(tr.weekday(wkd))
                text_row.append(' ')

            cal_cell.append(text_row)

            # Put dates
            for week in cal.monthdatescalendar(year, month):
                wk = cal_week_num(cal, week[0])
                text_row = TinyCalTableTextRow(wk)
                text_row.append(' ')
                for day in week:
                    text_row.append(day)
                    text_row.append(' ')

                cal_cell.append(text_row)

            cal_row.append(cal_cell)

    else:
        print('cont')
        print('start =', drange[0].to_date())
        print('end =  ', drange[1].to_date())
        print()

        cal_row = TinyCalTableRow()
        cal_table.append(cal_row)

        cal_cell = TinyCalTableCell('{sy}/{sm:02} ~ {ey}/{em:02}'.format(
            sy=drange[0].to_date().year,
            sm=drange[0].to_date().month,
            ey=drange[1].to_date().year,
            em=drange[1].to_date().month,
            ))
        cal_row.append(cal_cell)

        # Put Weekday header
        text_row = TinyCalTableTextRow(tr.weekday(-1))
        text_row.append(' ')
        for wkd in cal.iterweekdays():
            text_row.append(tr.weekday(wkd))
            text_row.append(' ')

        cal_cell.append(text_row)

        dcursor = drange[0].move_to_week_begin().to_date()

        while dcursor <= drange[1].to_date():
            wk = cal_week_num(cal, dcursor)

            text_row = TinyCalTableTextRow(wk)
            text_row.append(' ')

            for i in range(7):
                text_row.append(dcursor + timedelta(days=i))
                text_row.append(' ')

            cal_cell.append(text_row)

            dcursor += timedelta(days=7)

    return cal_table
