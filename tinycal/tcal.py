from __future__ import print_function

import calendar
import os.path

from . import CALRC
from .argparse import parser
from .config import TinyCalConfig
from .render import TableYear, TableMonth, render


def read_user_config():
    """
    :rtype: [(str, str)]
    """
    try:
        calrc = next(rc for rc in map(os.path.expanduser, CALRC) if os.path.exists(rc))
    except StopIteration:
        return []
    else:
        lines = filter(lambda l: l and not l.startswith('#'), map(str.strip, open(calrc)))
        return [tuple(map(str.strip, l.split('=', 1))) for l in lines]


def get_command_arguments():
    """
    :rtype: [(str, str)]
    """
    args = parser.parse_args().__dict__
    return [(k, v) for k, v in args.items() if v is not None]


def main():
    # Ref: https://stackoverflow.com/questions/16878315/what-is-the-right-way-to-treat-python-argparse-namespace-as-a-dictionary
    cfg = dict(read_user_config() + get_command_arguments())
    config = TinyCalConfig(cfg)

    cal = calendar.Calendar(firstweekday=calendar.MONDAY if config.start_monday else calendar.SUNDAY)
    table = TableYear()

    for m in config.range:
        table.add(TableMonth(cal, m))

    render(config, table)


if __name__ == '__main__':
    main()
