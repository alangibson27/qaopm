from processor_tests import TestHelper


class TestBcdAdjustment(TestHelper):
    def test_corrects_addition_correctly_with_half_carry(self):
        # given
        self._add_(0x08, 0x18)

        self.given_next_instruction_is(0x27)

        # when
        self.processor.execute()

        # then
        self.assert_register('a').equals(0x26)

        self.assert_flag('s').is_reset()
        self.assert_flag('z').is_reset()
        self.assert_flag('h').is_set()
        self.assert_flag('p').is_reset()
        self.assert_flag('c').is_reset()

    def test_corrects_addition_correctly_with_full_carry(self):
        # given
        self._add_(0x90, 0x90)

        self.given_next_instruction_is(0x27)

        # when
        self.processor.execute()

        # then
        self.assert_register('a').equals(0x80)

        self.assert_flag('s').is_set()
        self.assert_flag('z').is_reset()
        self.assert_flag('h').is_reset()
        self.assert_flag('p').is_reset()
        self.assert_flag('c').is_set()

    def test_corrects_addition_correctly_with_full_and_half_carry(self):
        # given
        self._add_(0x99, 0x99)

        self.given_next_instruction_is(0x27)

        # when
        self.processor.execute()

        # then
        self.assert_register('a').equals(0x98)

        self.assert_flag('s').is_set()
        self.assert_flag('z').is_reset()
        self.assert_flag('h').is_set()
        self.assert_flag('p').is_reset()
        self.assert_flag('c').is_set()

    def test_corrects_addition_correctly_with_no_carry(self):
        # given
        self._add_(0x09, 0x02)

        self.given_next_instruction_is(0x27)

        # when
        self.processor.execute()

        # then
        self.assert_register('a').equals(0x11)

        self.assert_flag('s').is_reset()
        self.assert_flag('z').is_reset()
        self.assert_flag('h').is_reset()
        self.assert_flag('p').is_set()
        self.assert_flag('c').is_reset()

    def test_corrects_subtraction_correctly_with_half_carry(self):
        # given
        self._sub_(0x10, 0x08)

        self.given_next_instruction_is(0x27)

        # when
        self.processor.execute()

        # then
        self.assert_register('a').equals(0x02)

        self.assert_flag('s').is_reset()
        self.assert_flag('z').is_reset()
        self.assert_flag('h').is_set()
        self.assert_flag('p').is_reset()
        self.assert_flag('c').is_reset()

    def test_corrects_subtraction_correctly_with_full_carry(self):
        # given
        self._sub_(0x79, 0x99)

        self.given_next_instruction_is(0x27)

        # when
        self.processor.execute()

        # then
        self.assert_register('a').equals(0x80)

        self.assert_flag('s').is_set()
        self.assert_flag('z').is_reset()
        self.assert_flag('h').is_reset()
        self.assert_flag('c').is_set()
        self.assert_flag('p').is_reset()

    def test_corrects_subtraction_correctly_with_full_and_half_carry(self):
        # given
        self._sub_(0x44, 0x88)

        self.given_next_instruction_is(0x27)

        # when
        self.processor.execute()

        # then
        self.assert_register('a').equals(0x56)

        self.assert_flag('s').is_reset()
        self.assert_flag('z').is_reset()
        self.assert_flag('h').is_set()
        self.assert_flag('c').is_set()
        self.assert_flag('p').is_set()

    def test_corrects_subtraction_correctly_with_no_carry(self):
        # given
        self._sub_(0x88, 0x44)

        self.given_next_instruction_is(0x27)

        # when
        self.processor.execute()

        # then
        self.assert_register('a').equals(0x44)

        self.assert_flag('s').is_reset()
        self.assert_flag('z').is_reset()
        self.assert_flag('h').is_reset()
        self.assert_flag('c').is_reset()
        self.assert_flag('p').is_set()

    def _add_(self, v1, v2):
        self.given_next_instruction_is(0x3e, v1)
        self.processor.execute()
        self.given_next_instruction_is(0xc6, v2)
        self.processor.execute()

    def _sub_(self, v1, v2):
        self.given_next_instruction_is(0x3e, v1)
        self.processor.execute()
        self.given_next_instruction_is(0xd6, v2)
        self.processor.execute()