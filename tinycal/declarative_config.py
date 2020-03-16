r"""
Declarative configuration parser

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


About variable names, `configparser` has more flexiblility than `argparse`,
however, `argparse` has more object-oriented for later usage.

`Config` API is inspired by `argparse` as usage below:

>>> class MyConfig(Config):
...     a = IntegerField(default=1)
...     b = BoolField(key='bb', default=True)
...     c = SelectorField(['en', 'zh'], key=lambda n: n*2, default='en')
...
>>> config = MyConfig({'bb': '0', 'cc': 'en'})
>>> config
MyConfig(a=1,b=False,c=en)
>>> config.c
'en'
"""


class ValidationError(Exception): pass


class ValueField(object):
    def __new__(cls, *args, **kwargs):
        kwarg_count = 0 if cls.__init__.__defaults__ is None else len(cls.__init__.__defaults__)
        arg_count = cls.__init__.__code__.co_argcount - 1 - kwarg_count
        assert len(args) == arg_count
        return super(ValueField, cls).__new__(cls)

    def __init__(self, default=None, limiters=()):
        self.default = default
        self.limiters = limiters

    def to_python(self, text):
        return text

    def limit(self, value):
        for lmtr in self.limiters:
            if not lmtr['condition'](value):
                return self.default

        return value

    def clean(self, key, text):
        if text is None:
            return self.default

        assert isinstance(text, str)

        try:
            value = self.to_python(text)
        except ValueError as e:
            value = self.default

        value = self.limit(value)

        return value


class IntegerField(ValueField):
    def to_python(self, text):
        try:
            value = int(text)
        except ValueError as e:
            return self.default

        return value


class BoolField(ValueField):
    mapping = {'true': True, '1': True, 'false': False, '0': False}

    def to_python(self, text):
        if text.lower() not in self.mapping:
            raise ValidationError('xxx')

        return self.mapping[text.lower()]


class SelectorField(ValueField):
    def __init__(self, choices, *args, **kwargs):
        assert all(isinstance(c, str) for c in choices)
        if 'default' in kwargs:
            assert isinstance(kwargs['default'], str)
        self.choices = choices
        super(SelectorField, self).__init__(*args, **kwargs)

    def limit(self, value):
        if value not in self.choices:
            return self.default

        return super(SelectorField, self).limit(value)
