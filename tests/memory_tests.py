from nose.tools import *
from z80.memory import Memory, MemoryException

class TestMemory:
    def setup(self):
        self.memory = Memory()

    def test_correct_size(self):
        assert_equal(len(self.memory.memory), 65536)

    def test_poke_and_peek(self):
        assert_equal(0, self.memory.peek(16384))
        self.memory.poke(16384, 128)
        assert_equal(128, self.memory.peek(16384))

    def test_peek_address_above_range(self):
        self.memory.poke(0x0000, 0xff)
        assert_equals(self.memory.peek(0xffff + 0x0001), 0xff)

    def test_peek_address_below_range(self):
        self.memory.poke(0xffff, 0xff)
        assert_equals(self.memory.peek(0x0000 - 0x0001), 0xff)

    def test_poke_address_above_range(self):
        self.memory.poke(0xffff + 0x0001, 0xff)
        assert_equals(self.memory.peek(0x0000), 0xff)

    def test_poke_address_below_range(self):
        self.memory.poke(0x0000 - 0x0001, 0xff)
        assert_equals(self.memory.peek(0xffff), 0xff)

    def test_poke_out_of_range_value(self):
        with assert_raises(MemoryException) as context:
            self.memory.poke(1, -1)
        assert_true("invalid value for poke" in context.exception)

        with assert_raises(MemoryException) as context:
            self.memory.poke(1, 256)
        assert_true("invalid value for poke" in context.exception)