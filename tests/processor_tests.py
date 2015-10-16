from nose.tools import *
from z80.memory import Memory
from z80.processor import Processor

class TestProcessor:
    def setup(self):
        self.memory = Memory()
        self.processor = Processor(self.memory)

    def test_single_cycle_register_loads(self):
        operations = [
            (0x7f, 'a', 'a'),
            (0x78, 'a', 'b'),
            (0x79, 'a', 'c'),
            (0x7a, 'a', 'd'),
            (0x7b, 'a', 'e'),
            (0x7c, 'a', 'f'),
            (0x7d, 'a', 'l'),

            (0x47, 'b', 'a'),
            (0x40, 'b', 'b'),
            (0x41, 'b', 'c'),
            (0x42, 'b', 'd'),
            (0x43, 'b', 'e'),
            (0x44, 'b', 'f'),
            (0x45, 'b', 'l'),

            (0x4f, 'c', 'a'),
            (0x48, 'c', 'b'),
            (0x49, 'c', 'c'),
            (0x4a, 'c', 'd'),
            (0x4b, 'c', 'e'),
            (0x4c, 'c', 'f'),
            (0x4d, 'c', 'l'),

            (0x57, 'd', 'a'),
            (0x50, 'd', 'b'),
            (0x51, 'd', 'c'),
            (0x52, 'd', 'd'),
            (0x53, 'd', 'e'),
            (0x54, 'd', 'f'),
            (0x55, 'd', 'l'),

            (0x5f, 'e', 'a'),
            (0x58, 'e', 'b'),
            (0x59, 'e', 'c'),
            (0x5a, 'e', 'd'),
            (0x5b, 'e', 'e'),
            (0x5c, 'e', 'f'),
            (0x5d, 'e', 'l'),

            (0x67, 'h', 'a'),
            (0x60, 'h', 'b'),
            (0x61, 'h', 'c'),
            (0x62, 'h', 'd'),
            (0x63, 'h', 'e'),
            (0x64, 'h', 'f'),
            (0x65, 'h', 'l'),

            (0x6f, 'l', 'a'),
            (0x68, 'l', 'b'),
            (0x69, 'l', 'c'),
            (0x6a, 'l', 'd'),
            (0x6b, 'l', 'e'),
            (0x6c, 'l', 'f'),
            (0x6d, 'l', 'l')
        ]

        for (op_code, destination, source) in operations:
            yield self.check_single_cycle_register_load, op_code, destination, source

    def check_single_cycle_register_load(self, op_code, destination, source):
        self.processor.main_registers[source] = 0xff
        self.memory.poke(0x0, op_code)

        self.processor.single_cycle()

        assert_equals(0x0001, self.processor.special_registers['pc'])
        assert_equals(0xff, self.processor.main_registers[destination])
        assert_equals(0xff, self.processor.main_registers[source])

    def test_single_cycle_register_loads_from_memory(self):
        operations = [
            (0x7e, 'a', 'hl'),
            (0x0a, 'a', 'bc'),
            (0x1a, 'a', 'de'),

            (0x46, 'b', 'hl'),
            (0x4e, 'c', 'hl'),
            (0x56, 'd', 'hl'),
            (0x5e, 'e', 'hl'),
            (0x66, 'h', 'hl'),
            (0x6e, 'l', 'hl')
        ]

        for (op_code, destination, source_register) in operations:
            yield self.check_single_cycle_register_load_from_memory, op_code, destination, source_register

    def check_single_cycle_register_load_from_memory(self, op_code, destination, source_register):
        self.processor.main_registers[source_register[0]] = 0xa0
        self.processor.main_registers[source_register[1]] = 0xa0

        self.memory.poke(0x0, op_code)
        self.memory.poke(0xa0a0, 0xaa)

        self.processor.single_cycle()

        assert_equals(0x0001, self.processor.special_registers['pc'])
        assert_equals(0xaa, self.processor.main_registers[destination])

    def test_ld_a_i(self):
        self.processor.special_registers['i'] = 0xff

        self.memory.poke(0x0, 0xed)
        self.memory.poke(0x1, 0x57)

        self.processor.single_cycle()

        assert_equals(0x0002, self.processor.special_registers['pc'])
        assert_equals(0xff, self.processor.main_registers['a'])