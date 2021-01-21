import configparser
import sys

from os.path import expanduser, exists

from .color import *
from .fields import *


class TinyCalConfig:
    col = IntegerField(default=3, limiters=[GreaterThanLimiter(0)])
    after = DisplayRangeMarginField(default=DisplayRangeMargin('0'))
    before = DisplayRangeMarginField(default=DisplayRangeMargin('0'))
    wk = BoolField(default=False)
    fill = BoolField(default=False)
    border_richness = SelectorField(('full', 'basic', 'none'), default='full')
    border_style = SelectorField(('ascii', 'single', 'bold', 'double'), default='single')
    border_weld = BoolField(default=True)
    firstweekday = SelectorField(('sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'), default='sunday')
    lang = SelectorField(['en', 'zh', 'jp'], default='en')
    marks = PathField(default=None)
    mode = SelectorField(['month', 'week'], default='month')

    month_hint_range = BoolField(default=None)
    month_hint_sep = BoolField(default=None)
    month_hint_text = BoolField(default=None)

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
    color_month_hint_range = ColorListField(default=[Color('none:none')])
    color_month_hint_text = ColorListField(default=[Color('none:none')])

    def __init__(self):
        for name, field in vars(self.__class__).items():
            if isinstance(field, ValueField):
                setattr(self, name, field.default)

    def __repr__(self):
        return 'TinyCalConfig(' + (', '.join(k + '=' + repr(v) for (k, v) in self.__dict__.items())) + ')'

    @classmethod
    def load_conf(cls, calrcs):
        for rc in calrcs:
            if isinstance(rc, str):
                rc = expanduser(rc)
                if not exists(rc):
                    continue

                c = configparser.ConfigParser()
                try:
                    c.read(rc)
                except configparser.MissingSectionHeaderError:
                    with open(rc) as f:
                        c.read_string('[default]\n' + f.read())

                return dict(c)

            elif isinstance(rc, dict):
                # For unittest

                if 'default' not in rc:
                    ret = {}
                    ret['default'] = rc
                    return ret

                return rc

            else:
                raise TypeError('Cannot read config from', rc)

        return {}

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
            try:
                my_value = getattr(self, key)
                field = getattr(self.__class__, key)
                new_value = field(value)
                if new_value is not None:
                    setattr(self, key, new_value)

            except AttributeError:
                pass

            except InvalidValueError:
                print('Invalid value for', key, ':', value, file=sys.stderr)
                pass

        return self
