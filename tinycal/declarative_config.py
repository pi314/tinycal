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

    def __init__(self, key=None, default=None, validators=()):
        # TOOD: assert `key` must a valid variable name in Python
        self.map_key = lambda name: name if key is None else key(name) if callable(key) else key
        self.default = default
        self.validators = validators

    def to_python(self, text):
        return text

    def validate(self, key, value):
        for v in self.validators:
            if not v['condition'](value):
                raise Exception(v['message_template'].format(**locals()))

    def clean(self, key, text):
        if text is None:
            return self.default

        assert isinstance(text, str)

        value = self.to_python(text)
        self.validate(key, value)
        return value


class IntegerField(ValueField):
    def to_python(self, text):
        try:
            value = int(text)
        except ValueError as e:
            raise ValidationError('....')
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

    def validate(self, key, value):
        if value not in self.choices:
            raise ValidationError('xxxx')
        super(SelectorField, self).validate(key, value)


class Config(object):
    def __init__(self, attrs):
        assert isinstance(attrs, dict)
        assert all(isinstance(k, str) and isinstance(v, str) for k,v in attrs.items())

        for name, field in vars(self.__class__).items():
            if isinstance(field, ValueField):
                key = field.map_key(name)
                setattr(self, name, field.clean(key, attrs.get(key)))

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, ','.join('%s=%s' % attr for attr in sorted(vars(self).items())))
