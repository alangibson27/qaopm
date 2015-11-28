from nose.tools import assert_equals
from random import randint

from z80.memory import Memory
from z80.processor import Processor


def random_byte():
    return randint(0x00, 0xff)


class TestHelper:
    def __init__(self):
        self.instruction_pointer = 0x0
        self.memory = Memory()
        self.processor = Processor(self.memory)

    def given_next_instruction_is(self, *args):
        for arg in args:
            if isinstance(arg, list):
                for sub_arg in arg:
                    self.poke_at_ip(sub_arg)
            else:
                self.poke_at_ip(arg)

    def poke_at_ip(self, byte):
        self.memory.poke(self.instruction_pointer, byte)
        self.instruction_pointer += 1

    def given_register_contains_value(self, register, value):
        if register == 'ix' or register == 'iy':
            self.processor.index_registers[register] = value
        else:
            self.processor.main_registers[register] = value

    def given_register_pair_contains_value(self, register_pair, value):
        self.processor.main_registers[register_pair[0]] = value >> 8
        self.processor.main_registers[register_pair[1]] = value & 0xff

    def given_alternate_register_pair_contains_value(self, register_pair, value):
        self.processor.alternate_registers[register_pair[0]] = value >> 8
        self.processor.alternate_registers[register_pair[1]] = value & 0xff

    def given_stack_pointer_is(self, address):
        self.processor.special_registers['sp'] = address

    def given_program_counter_is(self, address):
        self.processor.special_registers['pc'] = address
        self.instruction_pointer = address

    def assert_cycles_taken(self, cycles):
        assert_equals(self.processor.cycles, cycles)

    def assert_pc_address(self, address):
        assert_equals(self.processor.special_registers['pc'], address)