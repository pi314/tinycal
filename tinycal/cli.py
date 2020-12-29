"""
Define command line options
"""

from datetime import date
from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError, FileType, Action

from . import CALRCS
from . import __version__
from .fields import DisplayRangeMargin
from .config import TinyCalConfig


class ExtendAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest) or []
        items.extend(values)
        setattr(namespace, self.dest, items)


parser = ArgumentParser(
    description='tinycal: A Python implementation of cal utility.',
    prog='tcal',
    epilog='Configuration files: {}'.format(CALRCS),
    formatter_class=RawTextHelpFormatter,
    )

parser.add_argument('--version', '-v', action='version', version=__version__)

parser.add_argument('--col', dest='col', default=None, type=int,
                    help='Specify the column numbers.')

parser.add_argument('-A', dest='after', default=None, type=DisplayRangeMargin,
                    help='Display the number of months after the current month.')

parser.add_argument('-B', dest='before', default=None, type=DisplayRangeMargin,
                    help='Display the number of months before the current month.')

parser.add_argument('-3', action='store_true', dest='a1b1', default=None,
                    help='Equals to -A 1 -B 1.')

parser.add_argument('-w', '--wk', action='store_true', dest='wk', default=None,
                    help='Display week number.')
parser.add_argument('-W', '--no-wk', action='store_false', dest='wk', default=None,
                    help='Don`t display week number.')

border_richness_options = TinyCalConfig.border_richness.choices
border_style_options = TinyCalConfig.border_style.choices
border_weld_options = ('weld', 'noweld')
border_keywords = border_richness_options + border_style_options + border_weld_options
def border_style_comma_separated_str(s):
    ret = []
    for i in s.strip().split(','):
        i = i.strip()
        if i in border_keywords:
            ret.append(i)

        else:
            raise ArgumentTypeError(
                    "invalid keyword: '" + i + "'\nAvailable keywords: " + repr(border_keywords))

    return ret

parser.add_argument('-b', '--border', dest='border_keywords', type=border_style_comma_separated_str,
                    default=[], const='full', nargs='?', action=ExtendAction,
                    help='Comma separated keywords to describe borders.\nAvailable keywords: '+ ','.join(border_keywords))

parser.add_argument('-f', '--fill', action='store_true', dest='fill', default=None,
                    help='Fill every month into rectangle with previous/next month dates.')
parser.add_argument('-F', '--no-fill', action='store_false', dest='fill', default=None,
                    help='Don`t fill month into rectangle.')

parser.add_argument('--color', choices=['never', 'always', 'auto'], type=str,
                    default='auto', const='auto', nargs='?',
                    help='Enable/disable color output.')
parser.add_argument('-c', action='store_const', const='always', dest='color',
                    help='Enable color output, equals to --color=always')
parser.add_argument('-C', action='store_const', const='never', dest='color',
                    help='Disable color output, equals to --color=never')

parser.add_argument('-l', '--lang', choices=['jp', 'zh', 'en'], type=str,
                    help='Select the language used to display weekdays and month names.')

parser.add_argument('-j', action='store_const', const='jp', dest='lang',
                    help='Equals to --lang=jp.')

parser.add_argument('-z', action='store_const', const='zh', dest='lang',
                    help='Equals to --lang=zh.')

parser.add_argument('-e', action='store_const', const='en', dest='lang',
                    help='Equals to --lang=en.')

parser.add_argument('--firstweekday', dest='firstweekday', type=str,
                    choices=TinyCalConfig.firstweekday.choices,
                    default=TinyCalConfig.firstweekday.default,
                    help='Set the first day of the week.')

parser.add_argument('-m', '--mode', dest='mode', type=str,
                    choices=TinyCalConfig.mode.choices,
                    default=TinyCalConfig.mode.default,
                    help='Set month-based or week-based calender.')

parser.add_argument('--marks', type=FileType('r'), dest='marks', default=None,
                    help='Specify the date marking file.')

def full_date_str(today_str):
    try:
        return date(*map(int, today_str.split('/')))
    except (TypeError, ValueError) as e:
        raise ArgumentTypeError("format should be yyyy/mm/dd")

parser.add_argument('--today', type=full_date_str, default=None,
                    help='Date that treated as today in format yyyy/mm/dd, used for debugging.')

parser.add_argument('year', type=int, nargs='?', default=None,
                    help='Year to display.')

parser.add_argument('month', type=int, nargs='?', default=None,
                    help='Month to display. Must specified after year.')


def parse_args():
    # Do some post process to make up limitations of argparse
    # e.g. not easy to have multiple 'dest's

    args = parser.parse_args()

    if args.a1b1:
        args.after = DisplayRangeMargin('1')
        args.before = DisplayRangeMargin('1')

    delattr(args, 'a1b1')

    args.border_richness = None
    args.border_style = None
    args.border_weld = None
    for i in args.border_keywords:
        if i in border_richness_options:
            args.border_richness = i
        elif i in border_style_options:
            args.border_style = i
        elif i in border_weld_options:
            args.border_weld = (i == 'weld')

    delattr(args, 'border_keywords')

    return args
