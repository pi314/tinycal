r"""
>>> import configparser
>>> c = configparser.ConfigParser()
>>> c.read_string('[_]\n' + open('allcalrc').read())
>>> config = TinyCalConfig(dict(c['_']))
>>> config.col
3
>>> config.lang
'en'
>>> config.color_wk
"""

from .declarative_config import (
        Config, ValueField,
        IntegerField, BoolField, SelectorField,
        )


def greater_than(n):
    return {
            'condition': (lambda v: v > n),
            'message_template': ('{key} must be greater than %s, get {value}' % n),
            }


class Color:
    def __init__(self, color_setting):
        self.color_setting = color_setting

    def __repr__(self):
        return '%s(setting=%s)' % (self.__class__.__name__, self.color_setting)


class BaseColorField(ValueField):
    ...


class ColorField(BaseColorField):
    ...


class TinyCalConfig(Config):
    col = IntegerField(default=3, validators=[greater_than(0)])
    after = IntegerField(default=0, validators=[greater_than(-1)])
    before = IntegerField(default=0, validators=[greater_than(-1)])
    wk = BoolField(default=False)
    sep = BoolField(default=True)
    fill = BoolField(default=False)
    border = BoolField(default=True)
    start_monday = BoolField(default=False)
    lang = SelectorField(['zh', 'jp', 'en'], default='zh')

    color_wk = ColorField(default=Color('BLACK'))
    color_fill = ColorField(default=Color('BLACK'))
    color_title = ColorField(default=Color('none:none'))
    color_weekday = ColorField(default=Color('none:none'))
    color_weekday_sunday = ColorField(default=Color('none:none'))
    color_weekday_monday = ColorField(default=Color('none:none'))
    color_weekday_tuesday = ColorField(default=Color('none:none'))
    color_weekday_wednesday = ColorField(default=Color('none:none'))
    color_weekday_thursday = ColorField(default=Color('none:none'))
    color_weekday_friday = ColorField(default=Color('none:none'))
    color_weekday_saturday = ColorField(default=Color('none:none'))
    color_sunday = ColorField(default=Color('none:none'))
    color_monday = ColorField(default=Color('none:none'))
    color_tuesday = ColorField(default=Color('none:none'))
    color_wednesday = ColorField(default=Color('none:none'))
    color_thursday = ColorField(default=Color('none:none'))
    color_friday = ColorField(default=Color('none:none'))
    color_saturday = ColorField(default=Color('none:none'))
    color_today = ColorField(default=Color('none:white'))
