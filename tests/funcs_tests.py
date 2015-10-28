from nose.tools import *
from z80.funcs import twos_complement

class TestFuncs:

    def test_twos_complement(self):
        values = [
            (0b11111111, -1),
            (0b10000000, -128),
            (0b00000001, 1),
            (0b01111111, 127)
        ]

        for twos_complement_value, signed_value in values:
            yield self.check_twos_complement, twos_complement_value, signed_value

    def check_twos_complement(self, twos_complement_value, signed_value):
        assert_equals(twos_complement(twos_complement_value), signed_value)