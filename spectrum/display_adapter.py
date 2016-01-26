class DisplayAdapter:
    def __init__(self, memory):
        self.memory = memory
        self.inks = {}
        self.papers = {}

        for flash in [False, True]:
            for bright in [False, True]:
                for paper in range(0, 8):
                    for ink in range(0, 8):
                        attr = (flash << 7) | (bright << 6) | (paper << 3) | ink
                        colour = Colour(ink, paper, flash, bright)
                        self.inks[attr] = colour.ink_rgb
                        self.papers[attr] = colour.paper_rgb

    def update_display(self, screen):
        get_address_and_bit_position = self.get_address_and_bit_position
        inks = self.inks
        papers = self.papers
        display_memory = self.memory.block_peek(0x4000, 0x5b00)

        for x in xrange(0, 256):
            for y in xrange(0, 192):
                pixel_address, bit = get_address_and_bit_position(x, y)
                colour_address = 0x1800 + (0x20 * (y / 8)) + (x / 8)

                colour_value = display_memory[colour_address]
                if display_memory[pixel_address] & pow(2, bit) > 0:
                    screen[x][y] = inks[colour_value]
                else:
                    screen[x][y] = papers[colour_value]

    @staticmethod
    def get_address_and_bit_position(x, y):
        bit = x % 8
        x_offset = (x / 8)

        hi = y & 0b00111000
        lo = y & 0b00000111

        line = (hi >> 3) | (lo << 3)

        if y < 0x40:
            address_base = 0x0000
        elif y < 0x80:
            address_base = 0x0800
        else:
            address_base = 0x1000

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
        self.flash = flash
        self.bright = bright
        self.ink_rgb = self._rgb(ink)
        self.paper_rgb = self._rgb(paper)

    def _rgb(self, colour):
        colour_bytes = colour_masks[colour] & (0xffffff if self.bright else 0xaaaaaa)
        red = (colour_bytes & 0xff0000) >> 16
        green = (colour_bytes & 0x00ff00) >> 8
        blue = colour_bytes & 0x0000ff
        return red, green, blue
