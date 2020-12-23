import calendar

from datetime import date, timedelta


class Tr:
    data_en = {
            'weekday': ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su', 'WK'],
            'month': ['<Error>',
                'January', 'February', 'March',
                'April', 'May', 'June',
                'July', 'August', 'September',
                'October', 'November', 'December'],
            'month_abbr': ['<Error>',
                'Jan', 'Feb', 'Mar',
                'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep',
                'Oct', 'Nov', 'Dec'],
            }

    data_zh = {
            'weekday': ['一', '二', '三', '四', '五', '六', '日', '週'],
            'month': ['<Error>',
                '１月', '２月', '３月',
                '４月', '５月', '６月',
                '７月', '８月', '９月',
                '１０月', '１１月', '１２月'],
            }
    data_jp = {
            'weekday': ['月', '火', '水', '木', '金', '土', '日', '週'],
            'month': ['<Error>',
                '睦月 (１月)', '如月 (２月)', '彌生 (３月)',
                '卯月 (４月)', '皐月 (５月)', '水無月 (６月)',
                '文月 (７月)', '葉月 (８月)', '長月 (９月)',
                '神無月 (１０月)', '霜月 (１１月)', '師走 (１２月)'],
            }

    def __init__(self, lang):
        try:
            self.data = getattr(Tr, 'data_' + lang)
        except AttributeError:
            self.data = getattr(Tr, 'data_en')

    def month(self, month, abbr=False):
        if abbr and 'month_abbr' in self.data:
            key = 'month_abbr'
        else:
            key = 'month'
        return self.data[key][month]

    def weekday(self, weekday):
        return self.data['weekday'][weekday]


class DateCursor:
    def __init__(self, cal, year, month, day):
        self.cal = cal
        self.year = year
        self.month = month
        self.day = day

    @property
    def umn(self):
        return (self.year * 12) + (self.month - 1)

    @staticmethod
    def from_date(cal, d):
        return DateCursor(cal, d.year, d.month, d.day)

    def to_date(self):
        if self.day == -1:
            day = calendar.monthrange(self.year, self.month)[1]
        else:
            day = self.day

        return date(self.year, self.month, day)

    def __isub__(self, other):
        d = date(self.year, self.month, self.day)
        d -= timedelta(other)
        self.year = d.year
        self.month = d.month
        self.day = d.day
        return self

    def __iadd__(self, other):
        d = date(self.year, self.month, self.day)
        d += other
        self.year = d.year
        self.month = d.month
        self.day = d.day
        return self

    def move_back_n_month(self, months):
        umn = self.umn
        umn -= months
        self.year = umn // 12
        self.month = (umn % 12) + 1
        self.day = 1
        return self

    def move_forward_n_month(self, months):
        umn = self.umn
        umn += months
        self.year = umn // 12
        self.month = (umn % 12) + 1
        self.day = -1
        return self

    def move_to_week_begin(self):
        d = date(self.year, self.month, self.day) - timedelta(
                days=list(self.cal.iterweekdays()).index(
                    self.to_date().weekday()))
        self.year = d.year
        self.month = d.month
        self.day = d.day
        return self
