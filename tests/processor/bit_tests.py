from processor_tests import TestHelper
from random import randint
from z80.funcs import to_signed


class TestBitOperations(TestHelper):
    def test_bit_reg(self):
        values = [(0x40, 'b', 0), (0x41, 'c', 0), (0x42, 'd', 0), (0x43, 'e', 0), (0x44, 'h', 0), (0x45, 'l', 0), (0x47, 'a', 0),
                  (0x48, 'b', 1), (0x49, 'c', 1), (0x4a, 'd', 1), (0x4b, 'e', 1), (0x4c, 'h', 1), (0x4d, 'l', 1), (0x4f, 'a', 1),
                  (0x50, 'b', 2), (0x51, 'c', 2), (0x52, 'd', 2), (0x53, 'e', 2), (0x54, 'h', 2), (0x55, 'l', 2), (0x57, 'a', 2),
                  (0x58, 'b', 3), (0x59, 'c', 3), (0x5a, 'd', 3), (0x5b, 'e', 3), (0x5c, 'h', 3), (0x5d, 'l', 3), (0x5f, 'a', 3),
                  (0x60, 'b', 4), (0x61, 'c', 4), (0x62, 'd', 4), (0x63, 'e', 4), (0x64, 'h', 4), (0x65, 'l', 4), (0x67, 'a', 4),
                  (0x68, 'b', 5), (0x69, 'c', 5), (0x6a, 'd', 5), (0x6b, 'e', 5), (0x6c, 'h', 5), (0x6d, 'l', 5), (0x6f, 'a', 5),
                  (0x70, 'b', 6), (0x71, 'c', 6), (0x72, 'd', 6), (0x73, 'e', 6), (0x74, 'h', 6), (0x75, 'l', 6), (0x77, 'a', 6),
                  (0x78, 'b', 7), (0x79, 'c', 7), (0x7a, 'd', 7), (0x7b, 'e', 7), (0x7c, 'h', 7), (0x7d, 'l', 7), (0x7f, 'a', 7)]

        for op_code, reg, bit_pos in values:
            for bit_value in [True, False]:
                yield self.check_bit_reg, op_code, reg, bit_pos, bit_value

    def check_bit_reg(self, op_code, reg, bit_pos, bit_value):
        # given
        self.given_register_contains_value(reg, pow(2, bit_pos) if bit_value else 0)
        self.given_next_instruction_is(0xcb, op_code)

        # when
        self.processor.execute()

        # then
        self.assert_flag('z').equals(not bit_value)
        self.assert_flag('h').is_set()
        self.assert_flag('n').is_reset()

    def test_bit_hl_indirect(self):
        values = [(0x46, 0), (0x4e, 1),
                  (0x56, 2), (0x5e, 3),
                  (0x66, 4), (0x6e, 5),
                  (0x76, 6), (0x7e, 7)]

        for op_code, bit_pos in values:
            for bit_value in [True, False]:
                yield self.check_bit_hl_indirect, op_code, bit_pos, bit_value

    def check_bit_hl_indirect(self, op_code, bit_pos, bit_value):
        # given
        self.given_register_pair_contains_value('hl', 0x1234)
        self.memory.poke(0x1234, pow(2, bit_pos) if bit_value else 0)
        self.given_next_instruction_is(0xcb, op_code)

        # when
        self.processor.execute()

        # then
        self.assert_flag('z').equals(not bit_value)
        self.assert_flag('h').is_set()
        self.assert_flag('n').is_reset()

    def test_bit_indexed_indirect(self):
        regs = [(0xdd, 'ix'), (0xfd, 'iy')]
        for reg_op_code, reg in regs:
            values = [(0x46, 0), (0x4e, 1), (0x56, 2), (0x5e, 3), (0x66, 4), (0x6e, 5), (0x76, 6), (0x7e, 7)]
            for op_code, bit_pos in values:
                for bit_value in [True, False]:
                    yield self.check_bit_indexed_indirect, reg, reg_op_code, op_code, bit_pos, bit_value

    def check_bit_indexed_indirect(self, reg, reg_op_code, op_code, bit_pos, bit_value):
        # given
        offset = randint(0, 255)
        self.processor.index_registers[reg] = 0x1234
        self.memory.poke(0x1234 + to_signed(offset), pow(2, bit_pos) if bit_value else 0)
        self.given_next_instruction_is(reg_op_code, 0xcb, offset, op_code)

        # when
        self.processor.execute()

        # then
        self.assert_flag('z').equals(not bit_value)
        self.assert_flag('h').is_set()
        self.assert_flag('n').is_reset()
