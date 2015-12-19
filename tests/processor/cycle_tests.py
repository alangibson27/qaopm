from nose.tools import assert_equals
from processor_tests import TestHelper


class TestCycles(TestHelper):
    def test_execute_returns_correct_number_of_tstates_for_each_operation_type(self):
        # given
        self.given_next_instruction_is(0x03)

        # when
        tstates = self.processor.execute()

        # then
        assert_equals(op_code, [0x03])
