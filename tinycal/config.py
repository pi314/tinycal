import configparser

from os.path import expanduser, exists

from .color import *
from .fields import *


class TinyCalConfig:
    col = IntegerField(default=3, limiters=[GreaterThanLimiter(0)])
    after = DisplayRangeMarginField(default=DisplayRangeMargin('0'))
    before = DisplayRangeMarginField(default=DisplayRangeMargin('0'))
    wk = BoolField(default=False)
    fill = BoolField(default=False)
    border_richness = SelectorField(('full', 'basic', 'off'), default='full')
    border_style = SelectorField(('ascii', 'single', 'bold', 'double'), default='single')
    border_weld = BoolField(default=True)
    start_monday = BoolField(default=False)
    lang = SelectorField(['zh', 'jp', 'en'], default='en')
    marks = PathField(default=None)
    cont = BoolField(default=False)
    start_monday = BoolField(default=False)

    # Color:
    # modifiers ::= modifier | modifier " " modifiers
    # modifier ::= color_code | "brighter" | "italic" | "underline" | "strike" | "reverse"
    # color_code ::= ANSI_color | 256_color | RGB_color
    # ANSI_color ::= "black" | "red" | "green" | "yellow" | "blue" | "magenta" | "cyan" | "white" |
    #                 "BLACK" | "RED" | "GREEN" | "YELLOW" | "BLUE" | "MAGENTA" | "CYAN" | "WHITE"
    # 256_color ::= int8
    # RGB_color ::= 000000 ~ FFFFFF
    #
    # Examples:
    # red:green underline italic
    # reverse black

    color_border = ColorField(default=[Color('none:none')])
    color_wk = ColorField(default=[Color('BLACK')])
    color_fill = ColorField(default=[Color('BLACK')])
    color_title = ColorField(default=[Color('none:none')])
    color_weekday = ColorField(default=[Color('none:none')])
    color_weekday_sunday = ColorField(default=[Color('none:none')])
    color_weekday_monday = ColorField(default=[Color('none:none')])
    color_weekday_tuesday = ColorField(default=[Color('none:none')])
    color_weekday_wednesday = ColorField(default=[Color('none:none')])
    color_weekday_thursday = ColorField(default=[Color('none:none')])
    color_weekday_friday = ColorField(default=[Color('none:none')])
    color_weekday_saturday = ColorField(default=[Color('none:none')])
    color_sunday = ColorField(default=[Color('none:none')])
    color_monday = ColorField(default=[Color('none:none')])
    color_tuesday = ColorField(default=[Color('none:none')])
    color_wednesday = ColorField(default=[Color('none:none')])
    color_thursday = ColorField(default=[Color('none:none')])
    color_friday = ColorField(default=[Color('none:none')])
    color_saturday = ColorField(default=[Color('none:none')])
    color_today = ColorField(default=[Color('reverse')])
    color_today_wk = ColorField(default=[Color('brighter')])
    color_default = ColorField(default=Color('white:none'))

    def __init__(self):
        for name, field in vars(self.__class__).items():
            if isinstance(field, ValueField):
                setattr(self, name, field.default)

    def __repr__(self):
        return 'TinyCalConfig(' + (', '.join(k + '=' + repr(v) for (k, v) in self.__dict__.items())) + ')'

    @classmethod
    def parse_conf(cls, calrcs):
        for rc in calrcs:
            if isinstance(rc, str):
                rc = expanduser(rc)
                if not exists(rc):
                    continue

                c = configparser.ConfigParser()
                c.read(rc)
                return cls().merge(dict(c['default']))

            elif isinstance(rc, dict):
                return cls().merge(rc)

            else:
                raise TypeError('Cannot read config from', rc)

        return cls()

    def merge(self, attrs):
        # Map 'today.wk.color' to 'color_today_wk'
        tmp = {}
        for k, v in attrs.items():
            if k.endswith('.color'):
                tmp[ '_'.join(['color'] + k.split('.')[:-1]) ] = v
            else:
                tmp[k.replace('.', '_')] = v

        attrs = tmp

        for key, value in attrs.items():
            my_value = getattr(self, key)
            field = getattr(self.__class__, key)
            new_value = field(value)
            if new_value is not None:
                setattr(self, key, new_value)

        return self
