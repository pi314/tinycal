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
Color(fg=BLACK,bg=None)
>>> config.color_today
Color(fg=None,bg=white)
"""

from .declarative_config import (
        Config, ValueField, ValidationError,
        IntegerField, BoolField, SelectorField,
        )


def greater_than(n):
    return {
            'condition': (lambda v: v > n),
            'message_template': ('{key} must be greater than %s, get {value}' % n),
            }


class Color:
    definition = {
            'black': '0', 'red': '1', 'green': '2', 'yellow': '3',
            'blue': '4', 'magenta': '5', 'cyan': '6', 'white': '7',
            }

    def __init__(self, color_setting):
        import re
        patt = re.compile(r'^\s*(?P<fg>\w+)?\s*:?(?:\s*(?P<bg>\w+)\s*)?$')
        m = patt.match(color_setting)
        if m is None:
            raise ValueError
        self.fg = self.clean(m.group('fg'))
        self.bg = self.clean(m.group('bg'))

    def clean(self, setting):
        if setting is None or setting.lower() == 'none':
            return None
        if setting.lower() not in self.definition:
            raise ValueError('Not defined color setting %s' % setting)
        return setting if setting == setting.upper() else setting.lower()

    def __repr__(self):
        return '%s(fg=%s,bg=%s)' % (self.__class__.__name__, self.fg, self.bg)


class ColorField(ValueField):
    def __init__(self, *args, **kwargs):
        if 'key' not in kwargs:
            kwargs['key'] = lambda name: '.'.join((lambda t: t[1:]+t[0:1])(name.split('_')))
        super(ColorField, self).__init__(*args, **kwargs)

    def to_python(self, text):
        try:
            return Color(text)
        except ValueError as e:
            raise ValidationError('%r not match color setting pattern' % text)


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
