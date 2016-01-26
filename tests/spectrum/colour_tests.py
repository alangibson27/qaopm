from nose.tools import assert_equals
from spectrum.display_adapter import Colour


class TestColour:
    def test_non_bright_colours_return_correct_rgb(self):
        values = [(Colour(7, 0, False, False), 0xaa, 0xaa, 0xaa, 0x00, 0x00, 0x00),
                  (Colour(6, 1, False, False), 0xaa, 0xaa, 0x00, 0x00, 0x00, 0xaa),
                  (Colour(5, 2, False, False), 0x00, 0xaa, 0xaa, 0xaa, 0x00, 0x00),
                  (Colour(4, 3, False, False), 0x00, 0xaa, 0x00, 0xaa, 0x00, 0xaa)]
        for colour, ink_red, ink_green, ink_blue, paper_red, paper_green, paper_blue in values:
            yield self.check_colours_return_correct_rgb, \
                  colour, ink_red, ink_green, ink_blue, paper_red, paper_green, paper_blue

    def test_bright_colours_return_correct_rgb(self):
        values = [(Colour(7, 0, False, True), 0xff, 0xff, 0xff, 0x00, 0x00, 0x00),
                  (Colour(6, 1, False, True), 0xff, 0xff, 0x00, 0x00, 0x00, 0xff),
                  (Colour(5, 2, False, True), 0x00, 0xff, 0xff, 0xff, 0x00, 0x00),
                  (Colour(4, 3, False, True), 0x00, 0xff, 0x00, 0xff, 0x00, 0xff)]
        for colour, ink_red, ink_green, ink_blue, paper_red, paper_green, paper_blue in values:
            yield self.check_colours_return_correct_rgb, \
                  colour, ink_red, ink_green, ink_blue, paper_red, paper_green, paper_blue

    @staticmethod
    def check_colours_return_correct_rgb(colour, ink_red, ink_green, ink_blue, paper_red, paper_green, paper_blue):
        assert_equals(colour.ink_rgb, (ink_red, ink_green, ink_blue))
        assert_equals(colour.paper_rgb, (paper_red, paper_green, paper_blue))