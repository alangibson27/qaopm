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
            (0x4f, 'c', 'a'),
            (0x48, 'c', 'b'),
            (0x49, 'c', 'c'),
            (0x4a, 'c', 'd'),
            (0x4b, 'c', 'e'),
            (0x4c, 'c', 'f'),
            (0x4d, 'c', 'l'),
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
            (0x1a, 'a', 'de')
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