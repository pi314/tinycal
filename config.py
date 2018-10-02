r"""
Configuration Parser

It provide declarative base class `Config` which considers basic feature as below:

- read config file
- parse config content into dict
- convert value with types according to declaration of `Config`

and advanced feature as below:

- render config file
- allowing undeclared key-values is optional
- optional `required=True` for `Value`
- warn or raise error with sufficient information, for example, line number

Here is the flow chart::

    file -> content  -> dict
                          |
                          v
    file <- content* <- config -> engine


Usage:

    class TinyCalConfig(Config):
        col = Natural(default=3)

    def get_config_from_file(paths: [str]) -> TinyCalConfig: ...

    def get_config_from_args() -> TinyCalConfig: ...

    config = TinyCalConfig.merge(get_config_from_file(), get_config_from_args())

    config.col  # 3


Test:

>>> class Integer(Value):
...     def to_python(self, text):
...         return int(text)
...
>>> n = Integer(default=3, validators=[greater_than(0)])
>>> n.clean('3')
3
>>> n.clean('-1')
Traceback (most recent call last):
  ...
config.ValidationError
>>> class TinyCalConfig(Config):
...     column = Integer(default=3, validators=[greater_than(0)])
"""

class ValidationError(Exception):
    pass


def greater_than(number):
    def validator(value):
        if not (value > number):
            raise ValidationError
    return validator


class Value:
    def __init__(self, key=None, default=None, validators=()):
        self.key = key
        self.default = default
        self.validators = validators

    def to_python(self, text):
        return text

    def validate(self, value):
        for v in self.validators:
            v(value)

    def clean(self, text):
        value = self.to_python(text)
        self.validate(value)
        return value


class Config:
    def __init__(self, data):
        self.data = data


'''
class Color(Value):
    def __init__(self, key=None, default=None):
        pass
    def __str__(self):
        pass
    def clean(self, v):
        pass

class TinyCalConfig(Config):
    key1 = Int(default=0)
    key2 = Color()
    def validate(self):
        pass
'''
