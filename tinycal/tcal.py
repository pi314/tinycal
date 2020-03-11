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

weekday_codes = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

LANG = {
        'en': {
            'weekday': ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su', 'WK'],
            'month': ['<Error>',
                'January', 'February', 'March',
                'April', 'May', 'June',
                'July', 'August', 'September',
                'October', 'November', 'December'],
            },
        'zh': {
            'weekday': ['一', '二', '三', '四', '五', '六', '日', '週'],
            'month': ['<Error>',
                '１月', '２月', '３月',
                '４月', '５月', '６月',
                '７月', '８月', '９月',
                '１０月', '１１月', '１２月'],
            },
        'jp': {
            'weekday': ['月', '火', '水', '木', '金', '土', '日', '週'],
            'month': ['<Error>',
                '睦月 (１月)', '如月 (２月)', '彌生 (３月)',
                '卯月 (４月)', '皐月 (５月)', '水無月 (６月)',
                '文月 (７月)', '葉月 (８月)', '長月 (９月)',
                '神無月 (１０月)', '霜月 (１１月)', '師走 (１２月)'],
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


def calculate_week_of_the_year(first_date_of_year, target_date):
    return (target_date - first_date_of_year).days // 7 + 1


def main():
    conf = TinyCalConfig.parse_conf(CALRCS)
    args = parser.parse_args()

    border_args = args.border
    args.border = None
    args.border_style = None
    args.border_weld = None
    for i in border_args:
        if i in ('full', 'basic', 'off', 'false'):
            args.border = i
        elif i in ('ascii', 'single', 'bold', 'double'):
            args.border_style = i
        elif i in ('weld', 'noweld'):
            args.border_weld = (i == 'weld')

    # Merge args and conf in-place into conf
    for k in vars(conf):
        if k in vars(args) and getattr(args, k) is not None:
            setattr(conf, k , getattr(args, k))

    if conf.border == 'true':
        conf.border = 'full'
    elif conf.border == 'false':
        conf.border = 'off'

    # enable/disable coloring
    if (args.color == 'never') or (args.color == 'auto' and not stdout.isatty()):
        for k in vars(conf):
            if k.startswith('color_'):
                setattr(conf, k, Color(''))

    today = args.today if args.today else date.today()

    # Calculate display range (from which month to which month)
    if args.year is not None and args.month is None:
        month_leading_dates = [date(args.year, month, 1) for month in range(1, 13)]
    else:
        year = args.year or today.year
        month = args.month or today.month
        before, after = (1, 1) if args.a1b1 else (conf.before, conf.after)
        month_leading_dates = calculate_month_range(before, after, year, month)


    calendar = Calendar(MONDAY if conf.start_monday else SUNDAY)
    monthdates = calendar.monthdatescalendar

    # Create TinyCalRenderer object for rendering
    renderer = TinyCalRenderer(conf)

    # Colors are calculated *outside* the renderer
    # It's for contiguous mode
    def colorize_weekday(idx):
        color_name = 'color_weekday_%s' % weekday_codes[idx]
        color = getattr(conf, color_name)
        string = LANG[conf.lang]['weekday'][idx]
        return color(string) + conf.color_weekday.code if color else string

    weekday_text = conf.color_weekday(' '.join(map(colorize_weekday, calendar.iterweekdays())))

    def colorize_wk(wk):
        if isinstance(wk, int):
            return conf.color_wk('{:>2}'.format(wk))

        return conf.color_wk(wk)

    wk_text = colorize_wk(LANG[conf.lang]['weekday'][-1])

    month_range = [ld.month for ld in month_leading_dates]
    def colorize_day(day):
        if (not args.cont and day.month != ld.month) or (args.cont and day.month not in month_range):
            c = (conf.color_fill) if (conf.fill) else (lambda s: '  ')
        else:
            if day == today:
                c = conf.color_today
            else:
                c = getattr(conf, 'color_%s' % weekday_codes[day.weekday()])

        return c('{:>2}'.format(day.day))

    if args.cont:
        # For contiguous mode, only 1 Cell obj needed
        cells = [Cell(conf)]
        f = month_leading_dates[0]
        t = month_leading_dates[-1]
        if f == t:
            cell[0].title = '{m} {y}'.format(m=LANG[conf.lang]['month'][f.month], y=f.year)
        else:
            cells[0].title = '{}/{:02} ~ {}/{:02}'.format(f.year, f.month, t.year, t.month)
        cells[0].weekday_text = weekday_text
        cells[0].wk_text = wk_text

    else:
        # For non-contiguous mode, every month has its own Cell obj
        cells = []
        for ld in month_leading_dates:
            cell = Cell(conf)
            cell.title = '{m} {y}'.format(m=LANG[conf.lang]['month'][ld.month], y=ld.year)
            cell.weekday_text = weekday_text
            cell.wk_text = wk_text
            cells.append(cell)

    # Put the days into cells, and cells into renderer
    last_cell = None
    last_wk = None
    for ld in month_leading_dates:
        for idx, weeks in enumerate(monthdates(ld.year, ld.month)):
            days = []
            for day in weeks:
                days.append(colorize_day(day))

            week = calculate_week_of_the_year(monthdates(ld.year, 1)[0][0], ld) + idx

            # Dont append days into the same cell twice (ok for different cell)
            if (last_cell, last_wk) != (cells[0], week):
                cells[0].append(
                        wk=colorize_wk(week),
                        days=days
                        )
                last_wk = week
                last_cell = cells[0]

        if len(cells) > 1:
            renderer.append(cells.pop(0))

    assert len(cells) == 1
    renderer.append(cells[0])

    print(renderer.render())
