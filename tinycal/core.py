import sys

from . import CALRCS
from . import cli
from .config import TinyCalConfig, Color


def main():
    conf = TinyCalConfig.parse_conf(CALRCS)
    args = cli.parse_args()

    print(conf)
    print()
    print(args)
    print()

    # Remove arguments that are no part of TinyCalConfig
    month = args.month
    delattr(args, 'month')

    year = args.year
    delattr(args, 'year')

    color = args.color
    delattr(args, 'color')

    today = args.today
    delattr(args, 'today')

    conf.merge(args.__dict__)
    print(conf)
