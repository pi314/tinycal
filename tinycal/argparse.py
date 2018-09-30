"""
List command line options.
"""

from __future__ import absolute_import

from argparse import ArgumentParser, RawTextHelpFormatter

from . import CALRC


parser = ArgumentParser(
    description='tinycal: A Python implementation of cal utility.',
    prog='tcal',
    epilog='Configuration files: {}'.format(CALRC),
    formatter_class=RawTextHelpFormatter,
    )

parser.add_argument('--col', dest='col', default=None, type=int,
                    help='Specify the column numbers.')

parser.add_argument('-A', dest='after', default=None, type=int,
                    help='Display the number of months after the current month.')

parser.add_argument('-B', dest='before', default=None, type=int,
                    help='Display the number of months before the current month.')

parser.add_argument('-3', dest='a1b1', action='store_true', default=None,
                    help='Equals to -A 1 -B 1.')

parser.add_argument('-w', dest='wk', action='store_true', default=None,
                    help='Display week number.')
parser.add_argument('-W', dest='wk', action='store_false', default=None,
                    help='Don`t display week number.')

parser.add_argument('-s', '--sep', dest='sep', action='store_true', default=None,
                    help='Display separation lines.')
parser.add_argument('-S', '--no-sep', dest='sep', action='store_false', default=None,
                    help='Don`t display separation lines.')

parser.add_argument('-b', '--border', dest='border', action='store_true', default=None,
                    help='Display border lines.')
parser.add_argument('-nb', '--no-border', dest='border', action='store_false', default=None,
                    help='Don`t display border lines.')

parser.add_argument('-f', '--fill', dest='fill', action='store_true', default=None,
                    help='Fill every month into rectangle with previous/next month dates.')
parser.add_argument('-F', '--no-fill', dest='fill', action='store_false', default=None,
                    help='Don`t fill month into rectangle.')

parser.add_argument('-c', dest='color', action='store_true', default=None,
                    help='Enable VT100 color output.')
parser.add_argument('-C', dest='color', action='store_false', default=None,
                    help='Disable VT100 color output.')

parser.add_argument('-l', '--lang', dest='lang', default='en', choices=['jp', 'zh', 'en'], type=str,
                    help='Select the language used to display weekday.')

parser.add_argument('-j', dest='lang',action='store_const', const='jp',
                    help='Enable Japanese weekday names, equals to --lang=jp.')

parser.add_argument('-z', dest='lang',action='store_const', const='zh',
                    help='Enable Chinese weekday names, equals to --lang=zh.')

parser.add_argument('-e', dest='lang',action='store_const', const='en',
                    help='Enable Chinese weekday names, equals to --lang=en.')

parser.add_argument('-m', dest='start_monday', action='store_true', default=None,
                    help='Use Monday as first weekday.')
parser.add_argument('-M', dest='start_monday', action='store_false', default=None,
                    help='Use Sunday as first weekday.')

parser.add_argument('year', type=int, nargs='?', default=None,
                    help='Year to display.')

parser.add_argument('month', type=int, nargs='?', default=None,
                    help='Month to display. Must specified after year.')
