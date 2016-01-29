import os
from tempfile import NamedTemporaryFile

from nose.tools import *

from memory.memory import load_memory, save_memory, Memory, MemoryException


class TestMemory:
    def setup(self):
        self.memory = [0x00] * 0x10000

    # def test_correct_size(self):
    #     assert_equal(len(self.memory.memory), 65536)
    #
    # def test_poke_and_peek(self):
    #     assert_equal(0, self.memory.peek(16384))
    #     self.memory.poke(16384, 128)
    #     assert_equal(128, self.memory.peek(16384))
    #
    # def test_peek_address_above_range(self):
    #     self.memory.poke(0x0000, 0xff)
    #     assert_equals(self.memory.peek(0xffff + 0x0001), 0xff)
    #
    # def test_peek_address_below_range(self):
    #     self.memory.poke(0xffff, 0xff)
    #     assert_equals(self.memory.peek(0x0000 - 0x0001), 0xff)
    #
    # def test_poke_address_above_range(self):
    #     self.memory.poke(0xffff + 0x0001, 0xff)
    #     assert_equals(self.memory.peek(0x0000), 0xff)
    #
    # def test_poke_address_below_range(self):
    #     self.memory.poke(0x0000 - 0x0001, 0xff)
    #     assert_equals(self.memory.peek(0xffff), 0xff)
    #
    # def test_poke_out_of_range_value(self):
    #     with assert_raises(MemoryException) as context:
    #         self.memory.poke(1, -1)
    #     assert_true("invalid value for poke" in context.exception)
    #
    #     with assert_raises(MemoryException) as context:
    #         self.memory.poke(1, 256)
    #     assert_true("invalid value for poke" in context.exception)
    #
    # def test_block_peek(self):
    #     self.memory.poke(0xa000, 0x01)
    #     self.memory.poke(0xafff, 0x02)
    #     result = self.memory.block_peek(0xa000, 0xb000)
    #     assert_equals(len(result), 0x1000)
    #     assert_equals(result[0x000], 0x01)
    #     assert_equals(result[0xfff], 0x02)

    def test_read_into_memory(self):
        load_memory(self.memory, _this_directory() + '/test.rom', 0x1000)
        assert_equals(self.memory[0x1000], 0x3e)
        assert_equals(self.memory[0x1001], 0x05)
        assert_equals(self.memory[0x1002], 0x3c)

    def test_write_from_memory(self):
        self.memory[0x1000] = 0x3e
        self.memory[0x1001] = 0x05
        self.memory[0x1002] = 0x3c

        with NamedTemporaryFile() as outfile:
            save_memory(self.memory, outfile.name, 0x1000, 3)
            load_memory(self.memory, outfile.name, 0x2000)
            assert_equals(self.memory[0x1000], 0x3e)
            assert_equals(self.memory[0x1001], 0x05)
            assert_equals(self.memory[0x1002], 0x3c)


def _this_directory():
    return os.path.dirname(os.path.abspath(__file__))
