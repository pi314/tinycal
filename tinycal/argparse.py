"""
List command line options.
"""

from __future__ import absolute_import

from argparse import ArgumentParser, RawTextHelpFormatter

from . import CALRC_1ST, CALRC_2ND


parser = ArgumentParser(
    description='tinycal: A Python implementation of cal utility.',
    prog='tcal',
    epilog='\n'.join((
        'Configuration files:',
        '1st: {}'.format(CALRC_1ST),
        '2nd: {}'.format(CALRC_2ND),
        )),
    formatter_class=RawTextHelpFormatter,
    )

parser.add_argument('--col', dest='col', default=None, type=int,
                    help='Specify the column numbers.')

parser.add_argument('-A', dest='after', default=None, type=int,
                    help='Display the number of months after the current month.')

parser.add_argument('-B', dest='before', default=None, type=int,
                    help='Display the number of months before the current month.')

parser.add_argument('-3', action='store_true', dest='a1b1', default=None,
                    help='Equals to -A 1 -B 1.')

parser.add_argument('-w', action='store_true', dest='wk', default=None,
                    help='Display week number.')
parser.add_argument('-W', action='store_false', dest='wk', default=None,
                    help='Don`t display week number.')

parser.add_argument('-s', '--sep', action='store_true', dest='sep', default=None,
                    help='Display separation lines.')
parser.add_argument('-S', '--no-sep', action='store_false', dest='sep', default=None,
                    help='Don`t display separation lines.')

parser.add_argument('-b', '--border', action='store_true', dest='border', default=None,
                    help='Display border lines.')
parser.add_argument('-nb', '--no-border', action='store_false', dest='border', default=None,
                    help='Don`t display border lines.')

parser.add_argument('-f', '--fill', action='store_true', dest='fill', default=None,
                    help='Fill every month into rectangle with previous/next month dates.')
parser.add_argument('-F', '--no-fill', action='store_false', dest='fill', default=None,
                    help='Don`t fill month into rectangle.')

parser.add_argument('-c', action='store_true', dest='color', default=None,
                    help='Enable VT100 color output.')
parser.add_argument('-C', action='store_false', dest='color', default=None,
                    help='Disable VT100 color output.')

parser.add_argument('-l', '--lang', default='en', choices=['jp', 'zh', 'en'], type=str,
                    help='Select the language used to display weekday.')

parser.add_argument('-j', action='store_const', const='jp', dest='lang',
                    help='Enable Japanese weekday names, equals to --lang=jp.')

parser.add_argument('-z', action='store_const', const='zh', dest='lang',
                    help='Enable Chinese weekday names, equals to --lang=zh.')

parser.add_argument('-e', action='store_const', const='en', dest='lang',
                    help='Enable Chinese weekday names, equals to --lang=en.')

parser.add_argument('-m', action='store_true', dest='start_monday', default=None,
                    help='Use Monday as first weekday.')
parser.add_argument('-M', action='store_false', dest='start_monday', default=None,
                    help='Use Sunday as first weekday.')

parser.add_argument('year', type=int, nargs='?', default=None,
                    help='Year to display.')

parser.add_argument('month', type=int, nargs='?', default=None,
                    help='Month to display. Must specified after year.')
