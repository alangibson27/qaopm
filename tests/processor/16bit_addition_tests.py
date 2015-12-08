from processor_tests import TestHelper

class Test16BitAddition(TestHelper):
    def test_add_hl_and_other_reg_with_no_carry_or_half_carry(self):
        values = [(0x09, 'bc'), (0x19, 'de'), (0x39, 'sp')]
        for op_code, reg_pair in values:
            yield self.check_add_hl_with_no_carry_or_half_carry, op_code, reg_pair

    def check_add_hl_with_no_carry_or_half_carry(self, op_code, reg_pair):
        # given
        self.given_register_pair_contains_value('hl', 0x1111)
        self.given_register_pair_contains_value(reg_pair, 0x1111)

        self.given_next_instruction_is(op_code)

        # when
        self.processor.execute()

        # then
        self.assert_register_pair('hl').equals(0x2222)

        self.assert_flag('h').is_reset()
        self.assert_flag('n').is_reset()
        self.assert_flag('c').is_reset()

    def test_add_hl_to_itself_with_no_carry_or_half_carry(self):
        # given
        self.given_register_pair_contains_value('hl', 0x1111)

        self.given_next_instruction_is(0x29)

        # when
        self.processor.execute()

        # then
        self.assert_register_pair('hl').equals(0x2222)

        self.assert_flag('h').is_reset()
        self.assert_flag('n').is_reset()
        self.assert_flag('c').is_reset()


    def test_add_hl_and_bc_with_full_and_half_carry(self):
        # given
        self.given_register_pair_contains_value('hl', 0x1100)
        self.given_register_pair_contains_value('bc', 0xff00)

        self.given_next_instruction_is(0x09)

        # when
        self.processor.execute()

        # then
        self.assert_register_pair('hl').equals(0x1000)

        self.assert_flag('h').is_set()
        self.assert_flag('n').is_reset()
        self.assert_flag('c').is_set()

    def test_adc_hl_and_other_reg_with_no_carry_or_half_carry(self):
        values = [(0x4a, 'bc'), (0x5a, 'de'), (0x7a, 'sp')]
        for op_code, reg in values:
            for carry in [True, False]:
                yield self.check_adc_hl_and_other_reg_with_no_carry_or_half_carry, op_code, reg, carry

    def check_adc_hl_and_other_reg_with_no_carry_or_half_carry(self, op_code, reg, carry):
        # given
        self.given_register_pair_contains_value('hl', 0x1100)
        self.given_register_pair_contains_value(reg, 0x0011)
        self.processor.set_condition('c', carry)

        self.given_next_instruction_is(0xed, op_code)

        # when
        self.processor.execute()

        # then
        self.assert_register_pair('hl').equals(0x1111 + (1 if carry else 0))

        self.assert_flag('s').is_reset()
        self.assert_flag('z').is_reset()
        self.assert_flag('h').is_reset()
        self.assert_flag('p').is_reset()
        self.assert_flag('n').is_reset()
        self.assert_flag('c').is_reset()

    def test_adc_hl_with_bc_with_negative_result(self):
        # given
        self.given_register_pair_contains_value('hl', 0x7fff)
        self.given_register_pair_contains_value('bc', 0x0001)
        self.processor.set_condition('c', True)

        self.given_next_instruction_is(0xed, 0x4a)

        # when
        self.processor.execute()

        # then
        self.assert_register_pair('hl').equals(0x8001)

        self.assert_flag('s').is_set()
        self.assert_flag('z').is_reset()
        self.assert_flag('h').is_set()
        self.assert_flag('p').is_set()
        self.assert_flag('n').is_reset()
        self.assert_flag('c').is_reset()

    def test_adc_hl_with_bc_with_zero_result(self):
        # given
        self.given_register_pair_contains_value('hl', 0xfffe)
        self.given_register_pair_contains_value('bc', 0x0001)
        self.processor.set_condition('c', True)

        self.given_next_instruction_is(0xed, 0x4a)

        # when
        self.processor.execute()

        # then
        self.assert_register_pair('hl').equals(0x0000)

        self.assert_flag('s').is_reset()
        self.assert_flag('z').is_set()
        self.assert_flag('h').is_set()
        self.assert_flag('p').is_set()
        self.assert_flag('n').is_reset()
        self.assert_flag('c').is_set()