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
    firstweekday = SelectorField(('sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'), default='sunday')
    lang = SelectorField(['zh', 'jp', 'en'], default='en')
    marks = PathField(default=None)
    cont = BoolField(default=False)

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

    color_default = ColorListField(default=[Color('white:none')])
    color_border = ColorListField(default=[Color('none:none')])
    color_wk = ColorListField(default=[Color('BLACK')])
    color_fill = ColorListField(default=[Color('BLACK')])
    color_title = ColorListField(default=[Color('none:none')])
    color_weekday = ColorListField(default=[Color('none:none')])
    color_weekday_sunday = ColorListField(default=[Color('none:none')])
    color_weekday_monday = ColorListField(default=[Color('none:none')])
    color_weekday_tuesday = ColorListField(default=[Color('none:none')])
    color_weekday_wednesday = ColorListField(default=[Color('none:none')])
    color_weekday_thursday = ColorListField(default=[Color('none:none')])
    color_weekday_friday = ColorListField(default=[Color('none:none')])
    color_weekday_saturday = ColorListField(default=[Color('none:none')])
    color_sunday = ColorListField(default=[Color('none:none')])
    color_monday = ColorListField(default=[Color('none:none')])
    color_tuesday = ColorListField(default=[Color('none:none')])
    color_wednesday = ColorListField(default=[Color('none:none')])
    color_thursday = ColorListField(default=[Color('none:none')])
    color_friday = ColorListField(default=[Color('none:none')])
    color_saturday = ColorListField(default=[Color('none:none')])
    color_today = ColorListField(default=[Color('reverse')])
    color_today_wk = ColorListField(default=[Color('brighter')])

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
