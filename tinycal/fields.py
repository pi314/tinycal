import re

from os.path import expanduser

from .color import Color


class GreaterThanLimiter:
    def __init__(self, n):
        self.limit = n

    def __call__(self, value):
        return value > self.limit


class DisplayRangeMargin:
    def __init__(self, value):
        value = value.lower()
        m = re.match(r'^(\d+)([mw])?$', value)

        if not m:
            raise ValueError('Invalid display range:', value)

        self.value = int(m.group(1))
        self.unit = {'m': 'M', 'w': 'W'}.get(m.group(2), 'M')

    def __repr__(self):
        return str(self.value) + str(self.unit)


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
        try:
            value = int(value)
            for limiter in self.limiters:
                if not limiter(value):
                    raise ValueError('Value={} not in range'.format(value))

        except ValueError as e:
            return self.default

        return value


class DisplayRangeMarginField(ValueField):
    def gogo(self, value):
        return value


class StringField(ValueField):
    def gogo(self, value):
        return str(value)


class PathField(StringField):
    def gogo(self, value):
        return expanduser(value)


class SelectorField(StringField):
    def __init__(self, choices, default=None):
        super().__init__(default=default)
        self.choices = choices

    def gogo(self, value):
        if value not in self.choices:
            raise ValueError('Invalid value {} from choices {}'.format(value, repr(self.choices)))

        return value


class ColorField(StringField):
    def gogo(self, value):
        return list(map(Color, value.split()))
