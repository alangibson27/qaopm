from tests.processor.processor_tests import TestHelper


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