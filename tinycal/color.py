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

        self.name = s
        self.code = self.ansi_color_def[s.lower()]

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.name)


class Color:
    def __init__(self, modifier):
        self.fg = None
        self.bg = None
        self.bright = 0
        self.italic = False
        self.underline = False
        self.strike = False
        self.reverse = False

        if modifier in ('brighter', 'bright'):
            self.bright = 1

        elif modifier in ('darker', 'dim'):
            self.bright = -1

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
                self.fg = modifier

            else:
                self.fg, self.bg = modifier.split(':')
                self.bg = self.bg.lower()

            def value_normalize(v):
                # Filter out 'none' by mapping it to None
                if not v or v == 'none':
                    return None

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

                return None

            self.fg = value_normalize(self.fg)
            self.bg = value_normalize(self.bg)

            if isinstance(self.fg, ColorValueANSI):
                if self.fg.name.upper() == self.fg.name:
                    self.bright = 1
                    self.fg.name = self.fg.name.lower()

    def copy(self):
        ret = Color('')
        ret.fg = self.fg
        ret.bg = self.bg
        ret.bright = self.bright
        ret.italic = self.italic
        ret.underline = self.underline
        ret.strike = self.strike
        ret.reverse = self.reverse
        return ret

    def __add__(self, other):
        ret = self.copy()

        if not isinstance(other, Color):
            raise ValueError('Cannot add ' + other.__class__.__name__ + ' to Color')

        if other.reverse:
            ret.fg, ret.bg = ret.bg, ret.fg
            return ret

        if other.fg:
            ret.fg = other.fg

        if other.bg:
            ret.bg = other.bg

        if other.italic:
            ret.italic = other.italic

        if other.strike:
            ret.strike = other.strike

        if other.underline:
            ret.underline = other.underline

        ret.bright += other.bright

        if ret.bright > 1 and isinstance(ret.fg, ColorValueANSI) and ret.fg.name.lower() == 'black':
            ret.bright = 0
            ret.fg = ColorValueANSI('white')

        return ret

    def __call__(self, text):
        code = ''
        text = str(text)

        fg = self.fg
        bg = self.bg

        if bg and not fg:
            fg = ColorValueANSI('black')

        if self.bright >= 1:
            code += ';1'
        elif self.bright <= -1:
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
            'bright' if self.bright else '',
            ])) + ')'
