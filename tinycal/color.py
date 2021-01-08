import copy


class ColorValue256:
    def __init__(self, s):
        self.value = int(s)
        if self.value not in range(0, 256):
            raise ValueError(s, 'out of range')

    def __repr__(self):
        return '{}({})'.format(
                self.__class__.__name__,
                self.value,
                )


class ColorValueRGB:
    def __init__(self, s):
        if len(s) != 6:
            raise ValueError('len(' + s + ') != 6')

        v = int(s, 16)
        self.r = (v & 0xff0000) >> 16
        self.g = (v & 0x00ff00) >> 8
        self.b = (v & 0x0000ff)

    def __repr__(self):
        return '{}({:0>6X})'.format(
                self.__class__.__name__,
                (self.r << 16) | (self.g << 8) | self.b
                )


class ColorValueANSI:
    ansi_color_def = {
            'black': '0', 'red': '1', 'green': '2', 'yellow': '3',
            'blue': '4', 'magenta': '5', 'cyan': '6', 'white': '7',
            }

    def __init__(self, s):
        if s.lower() not in self.ansi_color_def:
            raise ValueError('Unknown ANSI color name', s)

        self.name = s.lower()
        self.bright = (s.upper() == s)

    @property
    def code(self):
        return self.ansi_color_def[self.name]

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.name.upper() if self.bright else self.name)

    def __add__(self, other):
        if isinstance(other, ColorValueEmpty):
            return self

        ret = copy.deepcopy(self)

        if isinstance(other, ColorValueBrighter):
            if ret.name == 'black' and ret.bright == 1:
                ret.name = 'white'
                ret.bright = 0
            else:
                ret.bright = min(self.bright + 1, 1)

            return ret

        elif isinstance(other, ColorValueDarker):
            if ret.name == 'white' and ret.bright == 0:
                ret.name = 'black'
                ret.bright = 1
            else:
                ret.bright = max(ret.bright - 1, 0)

            return ret

        return other


class ColorValueBrighter:
    def __repr__(self):
        return 'brighter'


class ColorValueDarker:
    def __repr__(self):
        return 'darker'


class ColorValueEmpty:
    def __add__(self, other):
        return other

    def __repr__(self):
        return 'empty'


class Color:
    def __init__(self, modifier):
        self.fg = ColorValueEmpty()
        self.bg = ColorValueEmpty()
        self.italic = False
        self.underline = False
        self.strike = False
        self.reverse = False

        if modifier in ('brighter', 'bright', 'brighter:', 'bright:'):
            self.fg = ColorValueBrighter()

        elif modifier in ('darker', 'dim', 'darker:', 'dim:'):
            self.fg = ColorValueDarker()

        elif modifier == 'italic':
            self.italic = True

        elif modifier == 'underline':
            self.underline = True

        elif modifier == 'strike':
            self.strike = True

        elif modifier in ('reverse', 'invert', 'inverse'):
            self.reverse = True

        else:
            # Parsing
            if ':' not in modifier:
                fg = modifier
                bg = None

            else:
                fg, bg = modifier.split(':')

            def value_normalize(v):
                if not v or (v == 'none'):
                    return ColorValueEmpty()

                try:
                    return ColorValueANSI(v)
                except ValueError:
                    pass

                try:
                    return ColorValue256(v)
                except ValueError:
                    pass

                try:
                    return ColorValueRGB(v)
                except ValueError:
                    pass

                return ColorValueEmpty()

            self.fg = value_normalize(fg)
            self.bg = value_normalize(bg)

    def __add__(self, other):
        ret = copy.deepcopy(self)

        # List[Color]
        if isinstance(other, (list, tuple)) and all(isinstance(o, Color) for o in other):
            return sum(other, start=ret)

        if not isinstance(other, Color):
            raise ValueError('Cannot add ' + other.__class__.__name__ + ' to Color')

        if other.reverse:
            ret.fg, ret.bg = ret.bg, ret.fg
            return ret

        ret.fg += other.fg
        ret.bg += other.bg

        if other.italic:
            ret.italic = other.italic

        if other.strike:
            ret.strike = other.strike

        if other.underline:
            ret.underline = other.underline

        return ret

    def __call__(self, text):
        code = ''
        text = str(text)

        fg = self.fg
        bg = self.bg

        if isinstance(fg, ColorValueEmpty) and not isinstance(bg, ColorValueEmpty):
            # Special case: none:color => black:color
            # It's because default fg is white
            fg = ColorValueANSI('black')

            # Special case: black:BLACK => black:white
            # It's because black bg is still black
            if bg.name == 'black' and bg.bright:
                bg.name = 'white'
                bg.bright = 0

        if isinstance(self.fg, ColorValueANSI):
            if self.fg.bright >= 1:
                code += ';1'
            else:
                code += ';0'

        if self.italic:
            code += ';3'

        if self.underline:
            code += ';4'

        if self.strike:
            code += ';9'

        # Foreground: ANSI color
        if isinstance(fg, ColorValueANSI):
            code += ';3' + fg.code

        # Foreground: 256 color
        elif isinstance(fg, ColorValue256):
            code += ';38;5;' + fg.value

        # Foreground: true color
        elif isinstance(fg, ColorValueRGB):
            code += ';38;2;' + str(fg.r) + ';' + str(fg.g) + ';' + str(fg.b)

        # Background: ANSI color
        if isinstance(bg, ColorValueANSI):
            code += ';4' + bg.code

        # Background: 256 color
        elif isinstance(bg, ColorValue256):
            code += ';48;5;' + bg.value

        # Background: true color
        elif isinstance(bg, ColorValueRGB):
            code += ';48;2;' + str(bg.r) + ';' + str(bg.g) + ';' + str(bg.b)

        if code:
            return ('\033[' + code.lstrip(';') + 'm') + text + '\033[m'
        else:
            return text


    def __repr__(self):
        return 'Color(' + ', '.join(filter(lambda x: x, [
            '' if not self.fg else 'fg=' + repr(self.fg),
            '' if not self.bg else 'bg=' + repr(self.bg),
            'reverse' if self.reverse else '',
            ])) + ')'
