"""
Core function of `tcal` command
"""

from __future__ import print_function

from calendar import Calendar, SUNDAY, MONDAY
from datetime import date
from sys import stdout

from . import CALRCS
from .cli import parser
from .render import TinyCalRenderer, Cell
from .config import TinyCalConfig, Color


LANG = {
        'weekday': {
            'jp': ['月', '火', '水', '木', '金', '土', '日'],
            'zh': ['一', '二', '三', '四', '五', '六', '日'],
            'en': ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'],
            'full': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
            },
        'month': {
            'jp': ['<Error>',
                '睦月 (１月)', '如月 (２月)', '彌生 (３月)',
                '卯月 (４月)', '皐月 (５月)', '水無月 (６月)',
                '文月 (７月)', '葉月 (８月)', '長月 (９月)',
                '神無月 (１０月)', '霜月 (１１月)', '師走 (１２月)'],
            'zh': ['<Error>',
                '１月', '２月', '３月',
                '４月', '５月', '６月',
                '７月', '８月', '９月',
                '１０月', '１１月', '１２月'],
            'en': ['<Error>',
                'January', 'February', 'March',
                'April', 'May', 'June',
                'July', 'August', 'September',
                'October', 'November', 'December'],
            },
        }


def calculate_month_range(before, after, year, month):
    r"""
    >>> calculate_month_range(1, 1, 2018, 1)
    [datetime.date(2017, 12, 1), datetime.date(2018, 1, 1), datetime.date(2018, 2, 1)]
    """
    return [date(year - (month <= i), (month - 1 - i) % 12 + 1, 1) for i in range(before, 0, -1)] + \
           [date(year, month, 1)] + \
           [date(year + (month + i > 12), (month - 1 + i) % 12 + 1, 1) for i in range(1, after+1)]


def main():
    conf = TinyCalConfig.parse_conf(CALRCS)
    args = parser.parse_args()

    # Merge args and conf in-place into conf
    for k in vars(conf):
        if k in vars(args) and getattr(args, k) is not None:
            setattr(conf, k , getattr(args, k))

    if conf.border == 'true':
        conf.border = 'full'

    # enable/disable coloring
    if (args.color == 'never') or (args.color == 'auto' and not stdout.isatty()):
        for k in vars(conf):
            if k.startswith('color_'):
                setattr(conf, k, Color(''))

    calendar = Calendar(MONDAY if conf.start_monday else SUNDAY)
    monthdates = calendar.monthdatescalendar

    def calculate_week_of_the_year(date):
        return (date - monthdates(date.year, 1)[0][0]).days // 7 + 1

    today = args.today if args.today else date.today()

    # Calculate display range (from which month to which month)
    if args.year is not None and args.month is None:
        month_leading_dates = [date(args.year, month, 1) for month in range(1, 13)]
    else:
        year = args.year or today.year
        month = args.month or today.month
        before, after = (1, 1) if args.a1b1 else (conf.before, conf.after)
        month_leading_dates = calculate_month_range(before, after, year, month)

    # Create TinyCalRenderer object for rendering
    renderer = TinyCalRenderer(conf)

    # Colors are calculated *outside* the renderer
    # It's for contiguous mode
    def colorize_weekday(idx):
        color_name = 'color_weekday_%s' % LANG['weekday']['full'][idx]
        color = getattr(conf, color_name)
        string = LANG['weekday'][conf.lang][idx]
        return color(string) + conf.color_weekday.code if color else string

    def colorize_wk(wk):
        return conf.color_wk('%2s' % wk)

    def colorize_day(day):
        if day.month != ld.month:
            if conf.fill:
                c = conf.color_fill
            else:
                c = lambda s: '  '
        else:
            if day == today:
                c = conf.color_today
            else:
                c = getattr(conf, 'color_%s' % LANG['weekday']['full'][day.weekday()])

        return c('{:>2}'.format(day.day))

    # Put the days into cells (month), and cells into renderer
    for ld in month_leading_dates:
        cell = Cell(conf)
        cell.title = '{m} {y}'.format(m=LANG['month'][conf.lang][ld.month], y=ld.year)

        cell.weekday_line = conf.color_weekday(' '.join(map(colorize_weekday, calendar.iterweekdays())))

        cell.wk = colorize_wk('WK')

        for idx, weeks in enumerate(monthdates(ld.year, ld.month)):
            days = []
            for day in weeks:
                days.append(colorize_day(day))

            cell.append(
                    wk=colorize_wk(calculate_week_of_the_year(ld) + idx),
                    days=days
                    )

        renderer.append(cell)

    print(renderer.render())
