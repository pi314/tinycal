from os.path import expanduser

from .color import Color


class ValueField:
    def __init__(self, default=None):
        self.default = default

    def __call__(self, value):
        if value is None:
            return None

        return self.gogo(value)


class BoolField(ValueField):
    mapping = {
            'true': True,
            'false': False,
            '1': True,
            '0': False,
            }

    def gogo(self, value):
        if isinstance(value, bool):
            return value

        if value.lower() in self.mapping:
            return self.mapping[value]

        return self.default


class IntegerField(ValueField):
    def __init__(self, default=None, limiters=()):
        super().__init__(default=default)
        self.limiters = limiters

    def gogo(self, value):
        if value is None:
            return self.default

        try:
            value = int(value)
            for limiter in self.limiters:
                if not limiter(value):
                    raise ValueError('Value={} not in range'.format(value))

        except ValueError as e:
            return self.default

        return value


class StringField(ValueField):
    def gogo(self, value):
        return str(value)


class PathField(StringField):
    def gogo(self, value):
        return expanduser(value)


class SelectorField(StringField):
    def __init__(self, choices, default=None):
        self.choices = choices
        super().__init__(default=default)

    def gogo(self, value):
        if value in self.choices:
            return value

        return self.default


class ColorField(StringField):
    def gogo(self, value):
        return Color(value)
