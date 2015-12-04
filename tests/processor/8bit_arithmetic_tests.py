import random
from tests.processor.processor_tests import TestHelper
from z80.funcs import to_signed

class Test8BitArithmeticGroup(TestHelper):
    def test_add_a_with_other_reg_giving_positive_result_with_no_carries_or_overflow(self):
        values = [('b', 0x80), ('c', 0x81), ('d', 0x82), ('e', 0x83), ('h', 0x84), ('l', 0x85)]
        for register, op_code in values:
            yield self.check_add_a_with_other_reg_giving_positive_result_with_no_carries_or_overflow, register, op_code

    def check_add_a_with_other_reg_giving_positive_result_with_no_carries_or_overflow(self, other_reg, op_code):
        # given
        self.given_register_contains_value('a', 0b00000100)
        self.given_register_contains_value(other_reg, 0b00000001)

        self.given_next_instruction_is(op_code)

        # when
        self.processor.execute()

        # then
        self.assert_register('a').equals(0b00000101)
        self.assert_register(other_reg).equals(0b00000001)

        self.assert_flag('s').is_reset()
        self.assert_flag('z').is_reset()
        self.assert_flag('h').is_reset()
        self.assert_flag('p').is_reset()
        self.assert_flag('n').is_reset()
        self.assert_flag('c').is_reset()

    def test_add_a_to_itself_giving_positive_result_with_no_carries_or_overflow(self):
        # given
        self.given_register_contains_value('a', 0b00000001)

        self.given_next_instruction_is(0x87)

        # when
        self.processor.execute()

        # then
        self.assert_register('a').equals(0b00000010)

        self.assert_flag('s').is_reset()
        self.assert_flag('z').is_reset()
        self.assert_flag('h').is_reset()
        self.assert_flag('p').is_reset()
        self.assert_flag('n').is_reset()
        self.assert_flag('c').is_reset()

    def test_add_a_with_other_reg_giving_positive_result_with_half_carry(self):
        # given
        self.given_register_contains_value('a', 0b00001000)
        self.given_register_contains_value('b', 0b00001000)

        self.given_next_instruction_is(0x80)

        # when
        self.processor.execute()

        # then
        self.assert_register('a').equals(0b00010000)
        self.assert_register('b').equals(0b00001000)

        self.assert_flag('s').is_reset()
        self.assert_flag('z').is_reset()
        self.assert_flag('h').is_set()
        self.assert_flag('p').is_reset()
        self.assert_flag('n').is_reset()
        self.assert_flag('c').is_reset()

    def test_add_a_to_itself_giving_zero_result(self):
        # given
        self.given_register_contains_value('a', 0)

        self.given_next_instruction_is(0x87)

        # when
        self.processor.execute()

        # then
        self.assert_register('a').equals(0)

        self.assert_flag('s').is_reset()
        self.assert_flag('z').is_set()
        self.assert_flag('h').is_reset()
        self.assert_flag('p').is_reset()
        self.assert_flag('n').is_reset()
        self.assert_flag('c').is_reset()

    def test_add_a_to_other_reg_giving_negative_result_and_overflow(self):
        # given
        self.given_register_contains_value('a', 0b01111000)
        self.given_register_contains_value('c', 0b01101001)

        self.given_next_instruction_is(0x81)

        # when
        self.processor.execute()

        # then
        self.assert_register('a').equals(0b11100001)
        self.assert_register('c').equals(0b01101001)

        self.assert_flag('s').is_set()
        self.assert_flag('z').is_reset()
        self.assert_flag('h').is_set()
        self.assert_flag('p').is_set()
        self.assert_flag('n').is_reset()
        self.assert_flag('c').is_reset()

    def test_add_a_to_other_reg_giving_full_carry(self):
        # given
        self.given_register_contains_value('a', 0b11111000)
        self.given_register_contains_value('d', 0b01101001)

        self.given_next_instruction_is(0x82)

        # when
        self.processor.execute()

        # then
        self.assert_register('a').equals(0b01100001)
        self.assert_register('d').equals(0b01101001)

        self.assert_flag('s').is_reset()
        self.assert_flag('z').is_reset()
        self.assert_flag('h').is_set()
        self.assert_flag('p').is_set()
        self.assert_flag('n').is_reset()
        self.assert_flag('c').is_set()

    def test_add_a_immediate(self):
        # given
        self.given_register_contains_value('a', 0b00001000)

        self.given_next_instruction_is(0xc6, 0b01000001)

        # when
        self.processor.execute()

        # then
        self.assert_register('a').equals(0b01001001)

        self.assert_flag('s').is_reset()
        self.assert_flag('z').is_reset()
        self.assert_flag('h').is_reset()
        self.assert_flag('p').is_reset()
        self.assert_flag('n').is_reset()
        self.assert_flag('c').is_reset()

    def test_add_a_hl_indirect(self):
        # given
        self.given_register_contains_value('a', 0b00001000)
        self.given_register_pair_contains_value('hl', 0xbeef)

        self.memory.poke(0xbeef, 0b01000001)

        self.given_next_instruction_is(0x86)

        # when
        self.processor.execute()

        # then
        self.assert_register('a').equals(0b01001001)

        self.assert_flag('s').is_reset()
        self.assert_flag('z').is_reset()
        self.assert_flag('h').is_reset()
        self.assert_flag('p').is_reset()
        self.assert_flag('n').is_reset()
        self.assert_flag('c').is_reset()

    def test_add_a_indexed_indirect(self):
        values = [('ix', [0xdd, 0x86]), ('iy', [0xfd, 0x86])]
        for register, op_codes in values:
            yield self.check_add_a_indexed_indirect, register, op_codes

    def check_add_a_indexed_indirect(self, register, op_codes):
        # given
        self.given_register_contains_value('a', 0b00001000)
        self.processor.index_registers[register] = 0xbeef

        offset = random.randint(0, 256)
        signed_offset = to_signed(offset)

        self.memory.poke(0xbeef + signed_offset, 0b01000001)

        self.given_next_instruction_is(op_codes, offset)

        # when
        self.processor.execute()

        # then
        self.assert_register('a').equals(0b01001001)

        self.assert_flag('s').is_reset()
        self.assert_flag('z').is_reset()
        self.assert_flag('h').is_reset()
        self.assert_flag('p').is_reset()
        self.assert_flag('n').is_reset()
        self.assert_flag('c').is_reset()
