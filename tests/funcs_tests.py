from nose.tools import *
from z80.funcs import *


class TestFuncs:
    def test_to_signed(self):
        values = [
            (0b11111111, -1),
            (0b10000000, -128),
            (0b00000001, 1),
            (0b01111111, 127)
        ]

        for unsigned_value, signed_value in values:
            yield self.check_to_signed, unsigned_value, signed_value

    def check_to_signed(self, unsigned_value, signed_value):
        assert_equals(to_signed(unsigned_value), signed_value)

    def test_to_signed_16bit(self):
        values = [
            (0b1011000111100000, -20000),
            (0b1111111111111111, -1),
            (0b0111111111111111, 32767)
        ]

        for unsigned_value, signed_value in values:
            yield self.check_to_signed_16bit, unsigned_value, signed_value

    def check_to_signed_16bit(self, unsigned_value, signed_value):
        assert_equals(to_signed_16bit(unsigned_value), signed_value)

    def test_to_hex_digits(self):
        result = to_hex_digits(0xfa)
        assert_equals(result, [0xf0, 0xa])

    def test_bitwise_add_with_no_full_carry_or_half_carry(self):
        values = [(0b00, 0b00, 0b00),
                  (0b00, 0b01, 0b01),
                  (0b00, 0b10, 0b10),
                  (0b00, 0b11, 0b11),
                  (0b01, 0b00, 0b01),
                  (0b01, 0b01, 0b10),
                  (0b01, 0b10, 0b11),
                  (0b01, 0b11, 0b100),
                  (0b10, 0b00, 0b10),
                  (0b10, 0b01, 0b11),
                  (0b10, 0b10, 0b100),
                  (0b10, 0b11, 0b101),
                  (0b11, 0b00, 0b11),
                  (0b11, 0b01, 0b100),
                  (0b11, 0b10, 0b101),
                  (0b11, 0b11, 0b110)]

        for v1, v2, expected in values:
            yield self.check_bitwise_add_with_no_full_carry_or_half_carry, v1, v2, expected

    def check_bitwise_add_with_no_full_carry_or_half_carry(self, v1, v2, expected):
        result = bitwise_add(v1, v2)
        assert_equals(result[0], expected)
        assert_false(result[1])
        assert_false(result[2])

    def test_bitwise_add_with_half_carry(self):
        result = bitwise_add(0b00001000, 0b00001000)
        assert_equals(result[0], 0b00010000)
        assert_true(result[1])
        assert_false(result[2])

    def test_bitwise_add_with_full_carry(self):
        result = bitwise_add(0b10000000, 0b10000000)
        assert_equals(result[0], 0b00000000)
        assert_false(result[1])
        assert_true(result[2])

    def test_bitwise_sub_with_no_full_borrow_or_half_borrow(self):
        values = [(0b11, 0b00, 0b11),
                  (0b11, 0b01, 0b10),
                  (0b11, 0b10, 0b01),
                  (0b11, 0b11, 0b00),
                  (0b10, 0b00, 0b10),
                  # (0b10, 0b01, 0b01),
                  (0b10, 0b10, 0b00)]
        for v1, v2, expected in values:
            yield self.check_bitwise_sub_with_no_full_borrow_or_half_borrow, v1, v2, expected

    def check_bitwise_sub_with_no_full_borrow_or_half_borrow(self, v1, v2, expected):
        result = bitwise_sub(v1, v2)
        assert_equals(result[0], expected)
        assert_false(result[2])
        assert_false(result[1])

    def test_bitwise_sub_with_full_borrow(self):
        result = bitwise_sub(0b00000000, 0b10000000)
        assert_equals(result[0], 0b10000000)
        assert_true(result[2])
        assert_false(result[1])

    def test_bitwise_sub_with_half_borrow(self):
        result = bitwise_sub(0b10000000, 0b00001000)
        assert_equals(result[0], 0b01111000)
        assert_false(result[2])
        assert_true(result[1])

    def test_bitwise_sub_with_full_and_half_borrow(self):
        result = bitwise_sub(0b00000000, 0b10001000)
        assert_equals(result[0], 0b01111000)
        assert_true(result[2])
        assert_true(result[1])

    def test_has_parity_with_even_parity(self):
        result = has_parity(0b10101010)
        assert_true(result)

    def test_has_parity_with_odd_parity(self):
        result = has_parity(0b00010000)
        assert_false(result)

    def test_bitwise_add_16bit_with_no_full_carry_or_half_carry(self):
        result, half_carry, full_carry = bitwise_add_16bit(0x1111, 0x2222)
        assert_equals(result, 0x3333)
        assert_false(half_carry)
        assert_false(full_carry)

    def test_bitwise_add_16bit_with_half_carry(self):
        result, half_carry, full_carry = bitwise_add_16bit(0x0111, 0x0f00)
        assert_equals(result, 0x1011)
        assert_true(half_carry)
        assert_false(full_carry)

    def test_bitwise_add_16bit_with_full_carry(self):
        result, half_carry, full_carry = bitwise_add_16bit(0x1000, 0xf111)
        assert_equals(result, 0x0111)
        assert_false(half_carry)
        assert_true(full_carry)

    def test_bitwise_add_16bit_with_full_and_half_carry(self):
        result, half_carry, full_carry = bitwise_add_16bit(0x1100, 0xff00)
        assert_equals(result, 0x1000)
        assert_true(half_carry)
        assert_true(full_carry)

    def test_bitwise_sub_16bit_with_no_borrow_or_half_borrow(self):
        result, half_borrow, full_borrow = bitwise_sub_16bit(0x1101, 0x0001)
        assert_equals(result, 0x1100)
        assert_false(half_borrow)
        assert_false(full_borrow)

    def test_bitwise_sub_16bit_with_half_borrow(self):
        result, half_borrow, full_borrow = bitwise_sub_16bit(0x1011, 0x0100)
        assert_equals(result, 0x0f11)
        assert_true(half_borrow)
        assert_false(full_borrow)

    def test_bitwise_sub_16bit_with_full_and_half_borrow(self):
        result, half_borrow, full_borrow = bitwise_sub_16bit(0x1011, 0x2100)
        assert_equals(result, 0xef11)
        assert_true(half_borrow)
        assert_true(full_borrow)
