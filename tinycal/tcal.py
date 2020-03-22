"""
Core function of `tcal` command
"""

from __future__ import print_function

import re
import sys

from calendar import Calendar, SUNDAY, MONDAY
from datetime import date
from os.path import expanduser
from sys import stdout, stderr

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
            'month_abbr': ['<Error>',
                'Jan', 'Feb', 'Mar',
                'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep',
                'Oct', 'Nov', 'Dec'],
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

date_mark_regex = re.compile(r'^(\d\d\d\d/\d\d/\d\d) +([\w:]+) *')


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

    if conf.color_today_wk == TinyCalConfig.color_today_wk.default:
        # If today.wk.color is not configured, and wk.color.fg is configured
        # Re-assign today.wk.color to a brighter version of wk.color
        if conf.color_wk.fg != None and conf.color_wk.bg == None:
            conf.color_today_wk = conf.color_wk.upper()
        else:
            conf.color_today_wk = conf.color_wk

    date_marks = {}
    if (args.color == 'never') or (args.color == 'auto' and not stdout.isatty()):
        # Disable coloring
        for k in vars(conf):
            if k.startswith('color_'):
                setattr(conf, k, Color(''))

    elif conf.marks:
        # Read date marking file
        try:
            with open(expanduser(conf.marks)) as marks_file:
                for line in marks_file:
                    m = date_mark_regex.match(line.strip())
                    if not m:
                        # Silently ignore invalid lines
                        continue

                    mark_date, mark_color = date(*map(int, m.group(1).split('/'))), m.group(2)
                    try:
                        date_marks[mark_date] = Color(mark_color)
                    except ValueError:
                        pass

        except FileNotFoundError:
            print('Warning: Mark file "{}" does not exist'.format(conf.marks), file=stderr)

    calendar = Calendar(MONDAY if conf.start_monday else SUNDAY)
    monthdates = calendar.monthdatescalendar

    today = args.today if args.today else date.today()
    today_wk = calculate_week_of_the_year(monthdates(today.year, 1)[0][0], today)

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
        color_name = 'color_weekday_%s' % weekday_codes[idx]
        color = getattr(conf, color_name)
        string = LANG[conf.lang]['weekday'][idx]
        return color(string) + conf.color_weekday.code if color else string

    weekday_title = conf.color_weekday(' '.join(map(colorize_weekday, calendar.iterweekdays())))

    def colorize_wk(wk, contain_today=False):
        if isinstance(wk, int):
            if contain_today:
                c = conf.color_today_wk
            else:
                c = conf.color_wk

            return c('{:>2}'.format(wk))

        return conf.color_wk(wk)

    wk_title = colorize_wk(LANG[conf.lang]['weekday'][-1])

    month_range = [ld.month for ld in month_leading_dates]

    month_abbr = {}
    for m in range(1, 13):
        month_abbr[m] = (LANG[conf.lang].get('month_abbr') or LANG[conf.lang]['month'])[m].split() + [''] * 5

    def colorize_day(day):
        if (not args.cont and day.month != ld.month) or (args.cont and day.month not in month_range):
            c = (conf.color_fill) if (conf.fill) else (lambda s: '  ')
        else:
            if day == today:
                c = conf.color_today
            elif day in date_marks:
                c = date_marks[day]
            else:
                c = getattr(conf, 'color_%s' % weekday_codes[day.weekday()])

        return c('{:>2}'.format(day.day))

    def get_month_abbr(month):
        if month not in month_range:
            return ''
        else:
            return month_abbr[month].pop(0)


    if args.cont:
        # For contiguous mode, only 1 Cell obj needed
        cells = [Cell(conf)]
        f = month_leading_dates[0]
        t = month_leading_dates[-1]
        if f == t:
            cells[0].title = '{m} {y}'.format(m=LANG[conf.lang]['month'][f.month], y=f.year)
            def get_month_abbr(month):
                return ''

        else:
            cells[0].title = '{}/{:02} ~ {}/{:02}'.format(f.year, f.month, t.year, t.month)

        cells[0].weekday_title = weekday_title
        cells[0].wk_title = wk_title

    else:
        # For non-contiguous mode, every month has its own Cell obj
        cells = []
        for ld in month_leading_dates:
            cell = Cell(conf)
            cell.title = '{m} {y}'.format(m=LANG[conf.lang]['month'][ld.month], y=ld.year)
            cell.weekday_title = weekday_title
            cell.wk_title = wk_title
            cells.append(cell)

        def get_month_abbr(month):
            return ''

    # Put the days into cells, and cells into renderer
    last_cell = None
    last_week_leading_date = None
    for ld in month_leading_dates:
        for week in monthdates(ld.year, ld.month):
            # calculate week number
            if args.cont and ld.month != week[-1].month and ld.year != today.year:
                # Edge case, sometimes wk53 needs to be changed to wk01
                wk = calculate_week_of_the_year(monthdates(week[-1].year, 1)[0][-1], week[-1])
            else:
                # Normal case
                wk = calculate_week_of_the_year(monthdates(ld.year, 1)[0][0], week[0])

            # Highlight current week
            if (not args.cont and today.month != ld.month) or (args.cont and today.month not in month_range):
                wk_contain_today = False
            else:
                wk_contain_today = today in week

            # Dont append days into the same cell twice (ok for different cell)
            if (last_cell, last_week_leading_date) != (cells[0], week[0]):
                cells[0].append(
                        wk=colorize_wk(wk, contain_today=wk_contain_today),
                        days=' '.join([colorize_day(day) for day in week]),
                        month=get_month_abbr(week[-1].month),
                        )
                last_week_leading_date = week[0]
                last_cell = cells[0]

        if len(cells) > 1:
            renderer.append(cells.pop(0))

    assert len(cells) == 1
    renderer.append(cells[0])

    print(renderer.render())
