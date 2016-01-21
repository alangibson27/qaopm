class DisplayAdapter:
    def __init__(self, memory):
        self.memory = memory
        self.colours = {}
        for flash in [False, True]:
            for bright in [False, True]:
                for paper in range(0, 8):
                    for ink in range(0, 8):
                        attr = (flash << 7) | (bright << 6) | (paper << 3) | ink
                        self.colours[attr] = Colour(ink, paper, flash, bright)

    def pixel_at(self, x, y):
        address, bit = self.get_address_and_bit_position(x, y)
        colour = self.colour_at(self.get_attribute_address(x, y))
        if self.memory.peek(address) & pow(2, bit) > 0:
            return colour.get_ink_rgb()
        else:
            return colour.get_paper_rgb()

    def colour_at(self, address):
        return self.colours[self.memory.peek(address)]

    @staticmethod
    def get_attribute_address(x, y):
        return 0x5800 + (0x20 * (y / 8)) + (x / 8)

    @staticmethod
    def get_address_and_bit_position(x, y):
        bit = x % 8
        x_offset = (x / 8)

        hi = y & 0b00111000
        lo = y & 0b00000111

        line = (hi >> 3) | (lo << 3)

        if y < 0x40:
            address_base = 0x4000
        elif y < 0x80:
            address_base = 0x4800
        else:
            address_base = 0x5000

        address = address_base + (line * 32) + x_offset
        return address, (7 - bit)

    @staticmethod
    def get_coordinate(address, bit):
        if address < 0x4800:
            y_base = 0
            address -= 0x4000
        elif address < 0x5000:
            y_base = 64
            address -= 0x4800
        else:
            y_base = 128
            address -= 0x5000

        line = address / 32

        hi = line & 0b00111000
        lo = line & 0b00000111

        y = y_base + ((hi >> 3) | (lo << 3))
        x = ((address % 32) * 8) + (7 - bit)
        return x, y


colour_masks = {
    0: 0x000000,
    1: 0x0000ff,
    2: 0xff0000,
    3: 0xff00ff,
    4: 0x00ff00,
    5: 0x00ffff,
    6: 0xffff00,
    7: 0xffffff
}


class Colour:
    def __init__(self, ink, paper, flash, bright):
        self.ink = ink
        self.paper = paper
        self.flash = flash
        self.bright = bright

    def get_ink_rgb(self):
        return self._rgb(self.ink)

    def get_paper_rgb(self):
        return self._rgb(self.paper)

    def _rgb(self, colour):
        colour_bytes = colour_masks[colour] & (0xffffff if self.bright else 0xaaaaaa)
        red = (colour_bytes & 0xff0000) >> 16
        green = (colour_bytes & 0x00ff00) >> 8
        blue = colour_bytes & 0x0000ff
        return red, green, blue
