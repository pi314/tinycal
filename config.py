r"""
Configuration Parser

It provide base class `Config` which considers basic feature as below:

- read config file
- parse config content into AST
- convert value with types according to declaration of `Config`
- warn or raise error with sufficient information, for example, line number

and advanced feature as below:

- render config file
- allowing undeclared key-values is optional

Here is the flow chart::

    file -> content  -> AST
                         |
                         v
    file <- content* <- config -> engine



It is declarative as below:

>>> class Color(Value):
...     def __init__(self, key=None, default=None):
...         pass
...     def convert(self, v):
...         pass

>>> class MyConfig(Config):
...     key1 = Int(default='...')
...     key2 = Color()
...     def validate(self):
...         pass

>>> config = MyConfig("......")
"""

from abc import ABCMeta, abstractmethod


# comes from `six` package for Python 2/3 compatible
def add_metaclass(metaclass):
    """Class decorator for creating a class with a metaclass."""
    def wrapper(cls):
        orig_vars = cls.__dict__.copy()
        slots = orig_vars.get('__slots__')
        if slots is not None:
            if isinstance(slots, str):
                slots = [slots]
            for slots_var in slots:
                orig_vars.pop(slots_var)
        orig_vars.pop('__dict__', None)
        orig_vars.pop('__weakref__', None)
        return metaclass(cls.__name__, cls.__bases__, orig_vars)
    return wrapper


@add_metaclass(ABCMeta)
class Value:
    @abstractmethod
    def convert(self):
        print(123)


class Config:
    def __init__(self, ast):
        pass
