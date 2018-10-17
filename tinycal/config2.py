r"""
>>> sample_config = '[_]\n' + open('allcalrc').read()
>>> try:
...     import configparser
...     c = configparser.ConfigParser()
...     c.read_string(sample_config)
...     config = TinyCalConfig(dict(c['_']))
... except:
...     import ConfigParser, io
...     c = ConfigParser.ConfigParser()
...     c.readfp(io.BytesIO(sample_config))
...     config = TinyCalConfig(dict(c.items('_')))
>>> config.col
3
>>> config.lang
'en'
>>> config.color_wk
Color(BLACK, None)
>>> config.color_today
Color(None, white)
"""

import re

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
    patt = re.compile(r'^\s*(?P<fg>\w+)?\s*:?(?:\s*(?P<bg>\w+)\s*)?$')
    definition = {
            'black': '0', 'red': '1', 'green': '2', 'yellow': '3',
            'blue': '4', 'magenta': '5', 'cyan': '6', 'white': '7',
            }

    def __init__(self, *color_setting):
        r"""
        >>> Color('a:b:c')
        Traceback (most recent call last):
          ....
        ValueError
        >>> Color('qwer')
        Traceback (most recent call last):
          ....
        ValueError: Undefined color "qwer"
        """
        if len(color_setting) == 0:
            self.fg = self.bg = None
        elif len(color_setting) == 1:
            m = self.patt.match(color_setting[0])
            if m is None:
                raise ValueError
            self.fg, self.bg = map(self.clean, m.groups())
        elif len(color_setting) == 2:
            self.fg, self.bg = map(self.clean, color_setting)
        else:
            raise ValueError

    def clean(self, setting):
        if setting is None or setting.lower() == 'none':
            return None

        if setting.lower() not in self.definition:
            raise ValueError('Undefined color "%s"' % setting)

        return setting.upper() if setting == setting.upper() else setting.lower()

    def __lshift__(self, new):
        r"""
        >>> Color('BLACK:RED') << Color(':WHITE')
        Color(BLACK, WHITE)
        """
        assert isinstance(new, Color)
        return Color(new.fg or self.fg, new.bg or self.bg)

    def __repr__(self):
        r"""
        >>> str(Color('BLACK'))
        'Color(BLACK, None)'
        """
        return '%s(%s, %s)' % (self.__class__.__name__, self.fg, self.bg)

    def __call__(self, item):
        r"""
        >>> Color()('raw string')
        'raw string'
        >>> Color(None,'white')(' * ')
        '\x1b[0;30;47m * \x1b[0m'
        >>> Color(None,'cyan')(' * ')
        '\x1b[46m * \x1b[0m'
        >>> Color('black',None)(' * ')
        '\x1b[0;30m * \x1b[0m'
        >>> Color('BLACK',None)(' * ')
        '\x1b[1;30m * \x1b[0m'
        >>> Color('black','white')(' * ')
        '\x1b[0;30;47m * \x1b[0m'
        """
        code = self.code
        reset = '\033[0m'
        if code:
            return '%s%s%s' % (code, item, reset)
        else:
            return '%s' % item

    @property
    def code(self):
        fgcode = lambda c: '3%s' % self.definition[c.lower()]
        bgcode = lambda c: '4%s' % self.definition[c]
        code = lambda *t: '\033[%sm' % ";".join(t)

        if self.fg is None:
            if self.bg is None:
                return ''
            elif self.bg == 'white':
                return code('0', fgcode('black'), bgcode('white'))  # reverse
            else:
                return code(bgcode(self.bg))  # keep foreground setting
        else:
            bright = '%i' % (self.fg == self.fg.upper())
            if self.bg is None:
                return code(bright, fgcode(self.fg))  # keep background setting
            else:
                return code(bright, fgcode(self.fg), bgcode(self.bg))


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
