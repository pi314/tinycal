from __future__ import print_function

import calendar
import os.path

from . import CALRC
from .argparse import parser
from .config import TinyCalConfig
from .render import TableYear, TableMonth, render


def parse_config(number, line):
    if '=' not in line:
        raise Exception('...')

    key, value = map(str.strip, line.split('=', 1))

    if key in ('col', 'after', 'before'):
        try:
            value_ = int(value)
        except ValueError:
            raise ValueError(number)

        if value_ < 0:
            raise ValueError(number)

        return key, value_

    if key in ('start_monday', 'border', 'fill', 'sep', 'wk'):
        if value.lower() not in ('true', 'false'):
            raise ValueError(number)
        return key, (value.lower() == 'true')

    if key == 'lang':
        if value not in ('en', 'jp', 'zh'):
            raise ValueError(number)
        return key, value

    if key in (
            'wk.color',
            'fill.color',
            'title.color',
            'weekday.color',
            'weekday.sunday.color',
            'weekday.monday.color',
            'weekday.tuesday.color',
            'weekday.wednesday.color',
            'weekday.thursday.color',
            'weekday.friday.color',
            'weekday.saturday.color',
            'sunday.color',
            'monday.color',
            'tuesday.color',
            'wednesday.color',
            'thursday.color',
            'friday.color',
            'saturday.color',
            'today.color',
            ):
        import re
        patt = re.compile(r'^\s*(?P<fg>\w+)?\s*:?(?:\s*(?P<bg>\w+)\s*)?$')
        if not patt.match(value):
            raise ValueError(number)
        return key, value

    raise ValueError(number)


def get_calrc():
    """
    :rtype: abs path | None
    """
    for rc in CALRC:
        calrc = os.path.expanduser(rc)
        if os.path.exists(rc):
            return calrc


def read_user_config():
    """
    :rtype: [(str, str)]
    """
    calrc = get_calrc()
    if calrc is None:
        return []

    # read lines and strip
    lines = ((n, l.strip()) for n, l in enumerate(open(calrc)))
    # remove empty or commented lines
    lines_ = ((n, l) for n, l in lines if l and not l.startswith('#'))
    # parse configuration lines
    config = (parse_config(n, l) for n, l in lines_)
    return list(config)


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
