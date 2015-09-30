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