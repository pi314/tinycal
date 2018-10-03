r"""
Configuration Parser


Features:

- consider all are key-value pairs
- all key-value pairs are optional
- all key-value pairs have default values
- all key-value pairs are validated by type and constraint
- provide object string, warn/info message for debugging


Here is the flow chart::

    file -> content  -> dict
                          |
                          v
    file <- content* <- config -> engine


Usage:

>>> current_year = current_month = 123
>>> class TinyCalConfig(Config):
...     column = Integer(default=3, validators=[greater_than(0)])
...     after = Integer(default=0, validators=[greater_than(-1)])
...     before = Integer(default=0, validators=[greater_than(-1)])
...
...     week_number = Bool(default=False)
...     seperator = Bool(default=True)
...     fill = Bool(default=False)
...     border = Bool(default=True)
...
...     month = Integer(default=current_month, validators=[valid_month])
...     year = Integer(default=current_year, validators=[valid_year])
...
...     lang = Selector(['zh', 'jp', 'en'], default='zh')
...
...     start_monday = Bool(default=False)
>>> config = TinyCalConfig({'column': '3'})
>>> config['column']
3
>>> config
TinyCalConfig(after=0,before=0,border=True,column=3,fill=False,lang=zh,month=123,seperator=True,start_monday=False,week_number=False,year=123)
>>> print(config)
TinyCalConfig(after=0,before=0,border=True,column=3,fill=False,lang=zh,month=123,seperator=True,start_monday=False,week_number=False,year=123)
"""

def greater_than(n):
    return {
            'condition': (lambda v: v > n),
            'message_template': ('{key} must be greater than %s, get {value}' % n),
            }

valid_month = {
        'condition': (lambda m: m in tuple(range(1, 13))),
        'message_template': 'month must be in 1..12, get {value}',
        }

valid_year = {
        'condition': (lambda y: y in tuple(range(1, 10000))),
        'message_template': 'year must be in 1..9999, get {value}',
        }


class ValidationError(Exception): pass


class Value(object):
    def __new__(cls, *args, **kwargs):
        kwarg_count = 0 if cls.__init__.__defaults__ is None else len(cls.__init__.__defaults__)
        arg_count = cls.__init__.__code__.co_argcount - 1 - kwarg_count
        assert len(args) == arg_count
        return super(Value, cls).__new__(cls)

    def __init__(self, key=None, default=None, validators=()):
        self.key = key
        self.default = default
        self.validators = validators

    def to_python(self, text):
        return text

    def validate(self, value):
        for v in self.validators:
            if not v['condition'](value):
                raise Exception(v['message_template'].format(**locals()))

    def clean(self, text):
        if text is None:
            return self.default

        assert isinstance(text, str)

        value = self.to_python(text)
        self.validate(value)
        return value


class Integer(Value):
    def to_python(self, text):
        try:
            value = int(text)
        except ValueError as e:
            raise ValidationError('....')
        return value


class Bool(Value):
    mapping = {'true': True, '1': True, 'false': False, '0': False}

    def to_python(self, text):
        if text.lower() not in self.mapping:
            raise ValidationError('xxx')

        return self.mapping[text.lower()]


class Selector(Value):
    def __init__(self, choices, *args, **kwargs):
        assert all(isinstance(c, str) for c in choices)
        self.choices = choices
        super(Selector, self).__init__(*args, **kwargs)

    def validate(self, value):
        if value not in self.choices:
            raise ValidationError('xxxx')
        super(Selector, self).validate(value)


class Config(object):
    def __init__(self, *settings):
        """
        Serve first comes setting
        """
        assert all(isinstance(attrs, dict) for attrs in settings)
        assert all(isinstance(k, str) and isinstance(v, str) for attrs in settings for k,v in attrs.items())

        attrs = dict(sum([tuple(s.items()) for s in reversed(settings)], ()))
        self._attrs = {name: field.clean(attrs.get(name))
                       for name, field in vars(self.__class__).items() if isinstance(field, Value)}

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, ','.join('%s=%s' % attr for attr in sorted(self._attrs.items())))

    def __getitem__(self, k):
        return self._attrs[k]
