r"""
>>> sample_config = '[_]\n' + open('allcalrc').read()
>>> try:
...     import configparser
...     c = configparser.ConfigParser()
...     c.read_string(sample_config)
...     #config = TinyCalConfig(dict(c['_']))
... except:
...     import ConfigParser, io
...     c = ConfigParser.ConfigParser()
...     c.readfp(io.BytesIO(sample_config))
...     #config = TinyCalConfig(dict(c.items('_')))
...
>>> config = TinyCalConfig(dict(c.items('_')))
>>> config.col
3
>>> config.lang
'en'
>>> config.color_wk
Color('BLACK:None')
>>> config.color_today
Color('None:white')
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
    definition = {
            'black': '0', 'red': '1', 'green': '2', 'yellow': '3',
            'blue': '4', 'magenta': '5', 'cyan': '6', 'white': '7',
            }
    patt = re.compile(r'^\s*(?P<fg>\w+)?\s*:?(?:\s*(?P<bg>\w+)\s*)?$')

    assert patt.match('').groups() == (None, None)
    assert patt.match('a').groups() == ('a', None)
    assert patt.match('a:').groups() == ('a', None)
    assert patt.match(':b').groups() == (None, 'b')
    assert patt.match('a:b').groups() == ('a', 'b')

    def __init__(self, color_setting):
        r"""
        >>> Color('red:red:red')
        Traceback (most recent call last):
          ....
        ValueError
        """
        m = self.patt.match(color_setting)
        if m is None:
            raise ValueError
        self.highlight, self.fg, self.bg = self.clean(*m.groups())

    def __len__(self):
        # use `__len__` instead of `__bool__` for Python 2/3 compatible
        return False if self.fg == self.bg == None else True

    def clean(self, fg, bg):
        r"""
        >>> Color('Apua')
        Traceback (most recent call last):
          ....
        ValueError: unrecognized foreground color: Apua
        """
        if fg is None or fg.lower() == 'none':
            fg_ = highlight = None
        else:
            fg_ = fg.lower()
            highlight = (fg_.upper() == fg)

        if bg is None or bg.lower() == 'none':
            bg_ = None
        else:
            bg_ = bg.lower()

        if fg_ is not None and fg_ not in self.definition:
            raise ValueError('unrecognized foreground color: {}'.format(fg))
        elif bg_ is not None and bg_ not in self.definition:
            raise ValueError('unrecognized background color: {}'.format(bg))

        return highlight, fg_, bg_

    def __str__(self):
        r"""
        >>> '%s' % Color('')
        'None:None'
        >>> '%s' % Color('BLACK:WHITE')
        'BLACK:white'
        """
        fg = self.fg.upper() if self.fg is not None and self.highlight else self.fg
        bg = self.bg
        return '%s:%s' % (fg, bg)

    def __lshift__(self, new):
        r"""
        >>> Color('BLACK:RED') << Color(':WHITE')
        Color('BLACK:white')
        """
        assert isinstance(new, Color)

        fg_color = self if new.fg is None else new
        bg_color = self if new.bg is None else new
        color = Color('')
        color.highlight, color.fg = fg_color.highlight, fg_color.fg
        color.bg = bg_color.bg
        return color

    def __repr__(self):
        r"""
        >>> Color('BLACK')
        Color('BLACK:None')
        >>> Color('')
        Color('None:None')
        """
        return "%s('%s')" % (self.__class__.__name__, self.__str__())

    def __call__(self, item):
        r"""
        >>> Color('')('raw string')
        'raw string'
        >>> Color('none:white')(' * ')
        '\x1b[0;30;47m * \x1b[0m'
        >>> Color('none:cyan')(' * ')
        '\x1b[46m * \x1b[0m'
        >>> Color('black:none')(' * ')
        '\x1b[0;30m * \x1b[0m'
        >>> Color('BLACK:none')(' * ')
        '\x1b[1;30m * \x1b[0m'
        >>> Color('black:white')(' * ')
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
            bright = '%i' % self.highlight
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
