from __future__ import print_function

import calendar
import os.path
from collections import namedtuple

from . import CALRC
from .argparse import parser
from .config import TinyCalConfig
from .render import TableYear, TableMonth, render


Line = namedtuple('Line', ['lineno', 'text'])


def parse_config(line):
    if '=' not in line.text:
        raise Exception(line.lineno)

    key, value = map(str.strip, line.text.split('=', 1))

    if key in ('col', 'after', 'before'):
        try:
            value_ = int(value)
        except ValueError:
            raise ValueError(line.lineno)

        if value_ < 0:
            raise ValueError(line.lineno)

        return key, value_

    if key in ('start_monday', 'border', 'fill', 'sep', 'wk'):
        if value.lower() not in ('true', 'false'):
            raise ValueError(line.lineno)
        return key, (value.lower() == 'true')

    if key == 'lang':
        if value not in ('en', 'jp', 'zh'):
            raise ValueError(line.lineno)
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
        # TODO: convert to None, coler, and existing fg/bg color
        if not patt.match(value):
            raise ValueError(line.lineno)

        return key, value

    raise ValueError(line.lineno)


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
    lines = (Line(n, t.strip()) for n, t in enumerate(open(calrc)))
    # remove empty or commented lines
    lines_ = (l for l in lines if l.text and not l.text.startswith('#'))
    # parse configuration lines
    config = (parse_config(l) for l in lines_)
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
        table.months.append(TableMonth(cal, m))

    render(config, table)


if __name__ == '__main__':
    main()
