from nose.tools import assert_equals
from random import randint

from z80.memory import Memory
from z80.processor import Processor
from z80.funcs import high_low_pair


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
        if register_pair == 'sp':
            self.processor.special_registers['sp'] = value
        elif register_pair[0] == 'i':
            self.processor.index_registers[register_pair] = value
        else:
            high_byte, low_byte = high_low_pair(value)
            self.processor.main_registers[register_pair[0]] = high_byte
            self.processor.main_registers[register_pair[1]] = low_byte

    def given_alt_register_pair_contains_value(self, register_pair, value):
        high_byte, low_byte = high_low_pair(value)
        self.processor.alternate_registers[register_pair[0]] = high_byte
        self.processor.alternate_registers[register_pair[1]] = low_byte

    def given_stack_pointer_is(self, address):
        self.processor.special_registers['sp'] = address

    def given_program_counter_is(self, address):
        self.processor.special_registers['pc'] = address
        self.instruction_pointer = address

    def assert_cycles_taken(self, cycles):
        assert_equals(self.processor.cycles, cycles)

    def assert_pc_address(self):
        return EqualsBuilder('pc', self.processor.special_registers['pc'])

    def assert_stack_pointer(self):
        return EqualsBuilder('sp', self.processor.special_registers['sp'])

    def assert_register(self, reg):
        return EqualsBuilder('reg ' + reg, self.processor.main_registers[reg])

    def assert_register_pair(self, reg_pair):
        value = self.processor.special_registers['sp'] if reg_pair == 'sp' else self.processor.get_16bit_reg(reg_pair)
        return EqualsBuilder('reg pair ' + reg_pair, value)

    def assert_alt_register_pair(self, reg_pair):
        return EqualsBuilder('alt reg pair ' + reg_pair, self.processor.get_16bit_alt_reg(reg_pair))

    def assert_flag(self, flag_name):
        return FlagSetBuilder(flag_name, self.processor.condition(flag_name))

    def assert_memory(self, address):
        return ContainsBuilder(self.memory.peek(address))


class EqualsBuilder:
    def __init__(self, object, value):
        self.object = object
        self.value = value

    def equals(self, expected):
        assert_equals(self.value, expected, '{} != {} (was {})'.format(self.object, expected, self.value))


class ContainsBuilder:
    def __init__(self, value):
        self.value = value

    def contains(self, expected):
        assert_equals(self.value, expected)


class FlagSetBuilder:
    def __init__(self, flag, value):
        self.flag = flag
        self.value = value

    def equals(self, expected):
        assert_equals(self.value, expected, 'flag {} not {}'.format(self.flag, 'set' if expected else 'reset'))

    def is_set(self):
        assert_equals(self.value, True, 'flag {} not set'.format(self.flag))

    def is_reset(self):
        assert_equals(self.value, False, 'flag {} not reset'.format(self.flag))