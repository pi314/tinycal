"""
Core function of `tcal` command
"""

from __future__ import print_function

from . import CALRCS
from .arguments import parser
from .config import TinyCalConfig
from .render import TinyCal


def main():
    conf = TinyCalConfig.parse_conf(CALRCS)
    args = parser.parse_args()
    print(TinyCal(conf, args).render())
