from __future__ import print_function

import calendar
import os.path

from . import CALRC_1ST, CALRC_2ND
from .argparse import parser
from .config import TinyCalConfig
from .render import TableYear, TableMonth, render


def read_user_config():
    calrc = ''
    calrc_2 = os.path.expanduser(CALRC_2ND)
    if os.path.exists(calrc_2):
        calrc = calrc_2

    calrc_1 = os.path.expanduser(CALRC_1ST)
    if os.path.exists(calrc_1):
        calrc = calrc_1

    user_config = {}
    if calrc:
        with open(calrc) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                key, value = line.split('=')
                key = key.strip()
                value = value.strip()
                user_config[key.lower()] = value

    return user_config


def main():
    args = parser.parse_args()

    cfg = {}
    cfg.update(read_user_config())
    cli_cfg = vars(args)
    cli_cfg = {key: cli_cfg[key] for key in cli_cfg if cli_cfg[key] is not None}
    cfg.update(cli_cfg)

    config = TinyCalConfig(cfg)

    cal = calendar.Calendar(firstweekday=calendar.MONDAY if config.start_monday else calendar.SUNDAY)
    table = TableYear()

    for m in config.range:
        table.add(TableMonth(cal, m))

    render(config, table)


if __name__ == '__main__':
    main()
