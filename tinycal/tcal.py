from __future__ import print_function

import os.path

from . import CALRC
from .argparse import parser
from .config2 import TinyCalConfig
from .render import TinyCal


def main():
    calrcs = [rc for rc in map(os.path.expanduser, CALRC) if os.path.exists(rc)]
    if calrcs:
        content = '[_]\n' + open(calrcs[0]).read()
        try:
            import configparser
            c = configparser.ConfigParser()
            c.read_string(content)
            kv = dict(c['_'])
        except:
            import ConfigParser, io
            c = ConfigParser.ConfigParser()
            c.readfp(io.BytesIO(content))
            kv = dict(c.items('_'))
    else:
        kv = {}

    conf = TinyCalConfig(kv)
    args = parser.parse_args()

    print(TinyCal(conf, args).render())


if __name__ == '__main__':
    main()
