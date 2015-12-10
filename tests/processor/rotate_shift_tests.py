from processor_tests import TestHelper


class TestRotateShift(TestHelper):
    def test_rlca(self):
        values = [(0b10101010, True,  0b01010101, True),
                  (0b10101010, False, 0b01010101, True),
                  (0b01010101, True,  0b10101010, False),
                  (0b01010101, False, 0b10101010, False)]

        for initial_acc, initial_carry, final_acc, final_carry in values:
            yield self.check_rotation, 0x07, initial_acc, initial_carry, final_acc, final_carry

    def test_rla(self):
        values = [(0b10101010, True,  0b01010101, True),
                  (0b10101010, False, 0b01010100, True),
                  (0b01010101, True,  0b10101011, False),
                  (0b01010101, False, 0b10101010, False)]

        for initial_acc, initial_carry, final_acc, final_carry in values:
            yield self.check_rotation, 0x17, initial_acc, initial_carry, final_acc, final_carry

    def test_rrca(self):
        values = [(0b10101010, True,  0b01010101, False),
                  (0b10101010, False, 0b01010101, False),
                  (0b01010101, True,  0b10101010, True),
                  (0b01010101, False, 0b10101010, True)]

        for initial_acc, initial_carry, final_acc, final_carry in values:
            yield self.check_rotation, 0x0f, initial_acc, initial_carry, final_acc, final_carry

    def test_rra(self):
        values = [(0b10101010, True,  0b11010101, False),
                  (0b10101010, False, 0b01010101, False),
                  (0b01010101, True,  0b10101010, True),
                  (0b01010101, False, 0b00101010, True)]

        for initial_acc, initial_carry, final_acc, final_carry in values:
            yield self.check_rotation, 0x1f, initial_acc, initial_carry, final_acc, final_carry

    def check_rotation(self, op_code, initial_acc, initial_carry, final_acc, final_carry):
        # given
        self.given_register_contains_value('a', initial_acc)
        self.processor.set_condition('c', initial_carry)

        self.given_next_instruction_is(op_code)

        # when
        self.processor.execute()

        # then
        self.assert_register('a').equals(final_acc)

        self.assert_flag('h').is_reset()
        self.assert_flag('n').is_reset()
        self.assert_flag('c').equals(final_carry)

    def test_rlc_reg(self):
        regs = [(0x00, 'b'), (0x01, 'c'), (0x02, 'd'), (0x03, 'e'), (0x04, 'h'), (0x05, 'l'), (0x07, 'a')]
        values = [(0b10101010, True,  0b01010101, True, False, False, True),
                  (0b10101010, False, 0b01010101, True, False, False, True),
                  (0b01010101, True,  0b10101010, False, True, False, True),
                  (0b01010101, False, 0b10101010, False, True, False, True),
                  (0b00000000, False, 0b00000000, False, False, True, True)]
        for op_code, reg in regs:
            for initial_acc, initial_carry, final_acc, final_carry, s, z, p in values:
                yield self.check_reg_rotation, reg, op_code, initial_acc, initial_carry, final_acc, final_carry, s, z, p

    def check_reg_rotation(self, reg, op_code, initial_acc, initial_carry, final_acc, final_carry, s, z, p):
        # given
        self.given_register_contains_value(reg, initial_acc)
        self.processor.set_condition('c', initial_carry)

        self.given_next_instruction_is(0xcb, op_code)

        # when
        self.processor.execute()

        # then
        self.assert_register(reg).equals(final_acc)

        self.assert_flag('s').equals(s)
        self.assert_flag('z').equals(z)
        self.assert_flag('h').is_reset()
        self.assert_flag('p').equals(p)
        self.assert_flag('n').is_reset()
        self.assert_flag('c').equals(final_carry)
