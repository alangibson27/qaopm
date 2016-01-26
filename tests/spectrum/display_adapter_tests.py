from nose.tools import assert_equals

from memory.memory import Memory
from spectrum.display_adapter import DisplayAdapter


class TestDisplayAdapter:
    def __init__(self):
        self.memory = Memory()
        self.display_adapter = DisplayAdapter(self.memory)

    # def test_memory_address_and_bit_position_maps_to_coordinate_correctly(self):
    #     values = [(0x0000, 7, 0, 0), (0x0001, 6, 9, 0), (0x57ff, 0, 255, 191)]
    #     for address, bit, x, y in values:
    #         yield self.check_memory_address_and_bit_position_maps_to_coordinate_correctly, address, bit, x, y
    #
    # def check_memory_address_and_bit_position_maps_to_coordinate_correctly(self, address, bit, x, y):
    #     # when
    #     coordinate = self.display_adapter.get_coordinate(address, bit)
    #
    #     # then
    #     assert_equals(coordinate, (x, y))
    #
    #     # and
    #     reverse_address, reverse_bit = self.display_adapter.get_address_and_bit_position(x, y)
    #     assert_equals(reverse_address, address)
    #     assert_equals(reverse_bit, bit)

    # def test_pixel_at_works(self):
    #     # given
    #     self.memory.poke(0x4000, 0b10100000)
    #     self.memory.poke(0x5800, 0x25)
    #
    #     # then
    #     assert_equals(self.display_adapter.pixel_at(0, 0), (0x00, 0xaa, 0xaa))
    #     assert_equals(self.display_adapter.pixel_at(1, 0), (0x00, 0xaa, 0x00))
    #     assert_equals(self.display_adapter.pixel_at(0, 0), (0x00, 0xaa, 0xaa))

    # def test_coordinate_maps_to_attribute_block(self):
    #     values = [(0, 0, 0x5800), (1, 0, 0x5800), (1, 1, 0x5800), (0, 8, 0x5820)]
    #     for x, y, address in values:
    #         yield self.check_coordinate_maps_to_attribute_block, x, y, address
    #
    # def check_coordinate_maps_to_attribute_block(self, x, y, address):
    #     assert_equals(self.display_adapter.get_attribute_address(x, y), address)

    # def test_colour_at_finds_correct_colours(self):
    #     values = [(0x00, (0x00, 0x00, 0x00), (0x00, 0x00, 0x00), False),
    #               (0x11, (0x00, 0x00, 0xaa), (0xaa, 0x00, 0x00), False)]
    #     for colour_byte, ink_colour, paper_colour, flash in values:
    #         yield self.check_colour_at_finds_correct_colours, colour_byte, ink_colour, paper_colour, flash
    #
    # def check_colour_at_finds_correct_colours(self, colour_byte, ink_colour, paper_colour, flash):
    #     # given
    #     self.memory.poke(0x5280, colour_byte)
    #
    #     # when
    #     colour = self.display_adapter.colour_at(0x5280)
    #
    #     # then
    #     assert_equals(colour.get_ink_rgb(), ink_colour)
    #     assert_equals(colour.get_paper_rgb(), paper_colour)
    #     assert_equals(colour.flash, flash)
