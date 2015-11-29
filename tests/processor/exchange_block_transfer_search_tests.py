from nose.tools import *

from tests.processor.processor_tests import TestHelper


class TestExchangeBlockTransferAndSearch(TestHelper):
    def test_ex_de_hl(self):
        # given
        self.given_register_pair_contains_value('de', 0x1234)
        self.given_register_pair_contains_value('hl', 0xabcd)

        self.given_next_instruction_is(0xeb)

        # when
        self.processor.execute()

        # then
        assert_equals(self.processor.main_registers['h'], 0x12)
        assert_equals(self.processor.main_registers['l'], 0x34)
        assert_equals(self.processor.main_registers['d'], 0xab)
        assert_equals(self.processor.main_registers['e'], 0xcd)

    def test_ex_af_alt_af(self):
        # given
        self.given_register_pair_contains_value('af', 0x1234)
        self.given_alternate_register_pair_contains_value('af', 0xabcd)

        self.given_next_instruction_is(0x08)

        # when
        self.processor.execute()

        # then
        assert_equals(self.processor.main_registers['a'], 0xab)
        assert_equals(self.processor.main_registers['f'], 0xcd)
        assert_equals(self.processor.alternate_registers['a'], 0x12)
        assert_equals(self.processor.alternate_registers['f'], 0x34)

    def test_exx(self):
        # given
        self.given_register_pair_contains_value('bc', 0x1234)
        self.given_alternate_register_pair_contains_value('bc', 0x4321)

        self.given_register_pair_contains_value('de', 0x5678)
        self.given_alternate_register_pair_contains_value('de', 0x8765)

        self.given_register_pair_contains_value('hl', 0x9abc)
        self.given_alternate_register_pair_contains_value('hl', 0xcba9)

        self.given_next_instruction_is(0xd9)

        # when
        self.processor.execute()

        # then
        assert_equals(self.processor.main_registers['b'], 0x43)
        assert_equals(self.processor.main_registers['c'], 0x21)
        assert_equals(self.processor.alternate_registers['b'], 0x12)
        assert_equals(self.processor.alternate_registers['c'], 0x34)

        assert_equals(self.processor.main_registers['d'], 0x87)
        assert_equals(self.processor.main_registers['e'], 0x65)
        assert_equals(self.processor.alternate_registers['d'], 0x56)
        assert_equals(self.processor.alternate_registers['e'], 0x78)

        assert_equals(self.processor.main_registers['h'], 0xcb)
        assert_equals(self.processor.main_registers['l'], 0xa9)
        assert_equals(self.processor.alternate_registers['h'], 0x9a)
        assert_equals(self.processor.alternate_registers['l'], 0xbc)

    def test_ex_sp_indirect_hl(self):
        # given
        self.given_stack_pointer_is(0xbeef)
        self.given_register_pair_contains_value('hl', 0x1234)

        self.memory.poke(0xbeef, 0xba)
        self.memory.poke(0xbef0, 0xbe)

        self.given_next_instruction_is(0xe3)

        # when
        self.processor.execute()

        # then
        assert_equals(self.memory.peek(0xbeef), 0x34)
        assert_equals(self.memory.peek(0xbef0), 0x12)

        assert_equals(self.processor.main_registers['h'], 0xbe)
        assert_equals(self.processor.main_registers['l'], 0xba)

    def test_ex_sp_indirect_index_reg(self):
        operations = [([0xdd, 0xe3], 'ix'), ([0xfd, 0xe3], 'iy')]
        for op_codes, register_pair in operations:
            yield self.check_ex_sp_indirect_index_reg, op_codes, register_pair

    def check_ex_sp_indirect_index_reg(self, op_codes, register_pair):
        # given
        self.given_stack_pointer_is(0xbeef)
        self.memory.poke(0xbeef, 0x12)
        self.memory.poke(0xbef0, 0x34)

        self.processor.index_registers[register_pair] = 0xbeba

        self.given_next_instruction_is(op_codes)

        # when
        self.processor.execute()

        # then
        assert_equals(self.memory.peek(0xbeef), 0xba)
        assert_equals(self.memory.peek(0xbef0), 0xbe)

        assert_equals(self.processor.index_registers[register_pair], 0x3412)

    def test_ldi_with_bc_decrementing_to_nonzero(self):
        # given
        self.given_register_pair_contains_value('hl', 0x1000)
        self.given_register_pair_contains_value('de', 0x2000)
        self.given_register_pair_contains_value('bc', 0xbeef)

        self.memory.poke(0x1000, 0xba)

        self.given_next_instruction_is(0xed, 0xa0)

        # when
        self.processor.execute()

        # then
        assert_equals(self.memory.peek(0x2000), 0xba)
        assert_equals(self.processor.main_registers['h'], 0x10)
        assert_equals(self.processor.main_registers['l'], 0x01)
        assert_equals(self.processor.main_registers['d'], 0x20)
        assert_equals(self.processor.main_registers['e'], 0x01)
        assert_equals(self.processor.main_registers['b'], 0xbe)
        assert_equals(self.processor.main_registers['c'], 0xee)

        assert_equals(self.processor.condition('h'), False)
        assert_equals(self.processor.condition('p'), True)
        assert_equals(self.processor.condition('n'), False)

    def test_ldi_with_bc_decrementing_to_zero(self):
        # given
        self.given_register_pair_contains_value('hl', 0x1000)
        self.given_register_pair_contains_value('de', 0x2000)
        self.given_register_pair_contains_value('bc', 0x0001)

        self.memory.poke(0x1000, 0xba)

        self.given_next_instruction_is(0xed, 0xa0)

        # when
        self.processor.execute()

        # then
        assert_equals(self.memory.peek(0x2000), 0xba)
        assert_equals(self.processor.main_registers['h'], 0x10)
        assert_equals(self.processor.main_registers['l'], 0x01)
        assert_equals(self.processor.main_registers['d'], 0x20)
        assert_equals(self.processor.main_registers['e'], 0x01)
        assert_equals(self.processor.main_registers['b'], 0x00)
        assert_equals(self.processor.main_registers['c'], 0x00)

        assert_equals(self.processor.condition('h'), False)
        assert_equals(self.processor.condition('p'), False)
        assert_equals(self.processor.condition('n'), False)

    def test_ldir_with_bc_greater_than_one(self):
        # given
        self.given_register_pair_contains_value('hl', 0x1000)
        self.given_register_pair_contains_value('de', 0x2000)
        self.given_register_pair_contains_value('bc', 0x000a)

        self.memory.poke(0x1000, 0xff)

        self.given_next_instruction_is(0xed, 0xb0)

        # when
        self.processor.execute()

        # then
        self.assert_pc_address(0x0000)
        assert_equals(self.memory.peek(0x2000), 0xff)
        assert_equals(self.processor.main_registers['h'], 0x10)
        assert_equals(self.processor.main_registers['l'], 0x01)
        assert_equals(self.processor.main_registers['d'], 0x20)
        assert_equals(self.processor.main_registers['e'], 0x01)
        assert_equals(self.processor.main_registers['b'], 0x00)
        assert_equals(self.processor.main_registers['c'], 0x09)

        assert_equals(self.processor.condition('h'), False)
        assert_equals(self.processor.condition('p'), False)
        assert_equals(self.processor.condition('n'), False)

    def test_ldir_with_bc_equal_to_one(self):
        # given
        self.given_register_pair_contains_value('hl', 0x1000)
        self.given_register_pair_contains_value('de', 0x2000)
        self.given_register_pair_contains_value('bc', 0x0001)

        self.memory.poke(0x1000, 0xff)

        self.given_next_instruction_is(0xed, 0xb0)

        # when
        self.processor.execute()

        # then
        self.assert_pc_address(0x0002)
        assert_equals(self.memory.peek(0x2000), 0xff)
        assert_equals(self.processor.main_registers['h'], 0x10)
        assert_equals(self.processor.main_registers['l'], 0x01)
        assert_equals(self.processor.main_registers['d'], 0x20)
        assert_equals(self.processor.main_registers['e'], 0x01)
        assert_equals(self.processor.main_registers['b'], 0x00)
        assert_equals(self.processor.main_registers['c'], 0x00)

        assert_equals(self.processor.condition('h'), False)
        assert_equals(self.processor.condition('p'), False)
        assert_equals(self.processor.condition('n'), False)

    def test_ldir_with_bc_equal_to_zero(self):
        # given
        self.given_register_pair_contains_value('hl', 0x1000)
        self.given_register_pair_contains_value('de', 0x2000)
        self.given_register_pair_contains_value('bc', 0x0000)

        self.memory.poke(0x1000, 0xff)

        self.given_next_instruction_is(0xed, 0xb0)

        # when
        self.processor.execute()

        # then
        self.assert_pc_address(0x0000)
        assert_equals(self.memory.peek(0x2000), 0xff)
        assert_equals(self.processor.main_registers['h'], 0x10)
        assert_equals(self.processor.main_registers['l'], 0x01)
        assert_equals(self.processor.main_registers['d'], 0x20)
        assert_equals(self.processor.main_registers['e'], 0x01)
        assert_equals(self.processor.main_registers['b'], 0xff)
        assert_equals(self.processor.main_registers['c'], 0xff)

        assert_equals(self.processor.condition('h'), False)
        assert_equals(self.processor.condition('p'), False)
        assert_equals(self.processor.condition('n'), False)

    def test_ldd_with_bc_decrementing_to_nonzero(self):
        # given
        self.given_register_pair_contains_value('hl', 0x1000)
        self.given_register_pair_contains_value('de', 0x2000)
        self.given_register_pair_contains_value('bc', 0xbeef)

        self.memory.poke(0x1000, 0xba)

        self.given_next_instruction_is(0xed, 0xa8)

        # when
        self.processor.execute()

        # then
        assert_equals(self.memory.peek(0x2000), 0xba)
        assert_equals(self.processor.main_registers['h'], 0x0f)
        assert_equals(self.processor.main_registers['l'], 0xff)
        assert_equals(self.processor.main_registers['d'], 0x1f)
        assert_equals(self.processor.main_registers['e'], 0xff)
        assert_equals(self.processor.main_registers['b'], 0xbe)
        assert_equals(self.processor.main_registers['c'], 0xee)

        assert_equals(self.processor.condition('h'), False)
        assert_equals(self.processor.condition('p'), True)
        assert_equals(self.processor.condition('n'), False)

    def test_ldd_with_bc_decrementing_to_zero(self):
        # given
        self.given_register_pair_contains_value('hl', 0x1000)
        self.given_register_pair_contains_value('de', 0x2000)
        self.given_register_pair_contains_value('bc', 0x0001)

        self.memory.poke(0x1000, 0xba)

        self.given_next_instruction_is(0xed, 0xa8)

        # when
        self.processor.execute()

        # then
        assert_equals(self.memory.peek(0x2000), 0xba)
        assert_equals(self.processor.main_registers['h'], 0x0f)
        assert_equals(self.processor.main_registers['l'], 0xff)
        assert_equals(self.processor.main_registers['d'], 0x1f)
        assert_equals(self.processor.main_registers['e'], 0xff)
        assert_equals(self.processor.main_registers['b'], 0x00)
        assert_equals(self.processor.main_registers['c'], 0x00)

        assert_equals(self.processor.condition('h'), False)
        assert_equals(self.processor.condition('p'), False)
        assert_equals(self.processor.condition('n'), False)

    def test_lddr_with_bc_greater_than_one(self):
        # given
        self.given_register_pair_contains_value('hl', 0x1000)
        self.given_register_pair_contains_value('de', 0x2000)
        self.given_register_pair_contains_value('bc', 0x000a)

        self.memory.poke(0x1000, 0xff)

        self.given_next_instruction_is(0xed, 0xb8)

        # when
        self.processor.execute()

        # then
        self.assert_pc_address(0x0000)
        assert_equals(self.memory.peek(0x2000), 0xff)
        assert_equals(self.processor.main_registers['h'], 0x0f)
        assert_equals(self.processor.main_registers['l'], 0xff)
        assert_equals(self.processor.main_registers['d'], 0x1f)
        assert_equals(self.processor.main_registers['e'], 0xff)
        assert_equals(self.processor.main_registers['b'], 0x00)
        assert_equals(self.processor.main_registers['c'], 0x09)

        assert_equals(self.processor.condition('h'), False)
        assert_equals(self.processor.condition('p'), False)
        assert_equals(self.processor.condition('n'), False)

    def test_lddr_with_bc_equal_to_one(self):
        # given
        self.given_register_pair_contains_value('hl', 0x1000)
        self.given_register_pair_contains_value('de', 0x2000)
        self.given_register_pair_contains_value('bc', 0x0001)

        self.memory.poke(0x1000, 0xff)

        self.given_next_instruction_is(0xed, 0xb8)

        # when
        self.processor.execute()

        # then
        self.assert_pc_address(0x0002)
        assert_equals(self.memory.peek(0x2000), 0xff)
        assert_equals(self.processor.main_registers['h'], 0x0f)
        assert_equals(self.processor.main_registers['l'], 0xff)
        assert_equals(self.processor.main_registers['d'], 0x1f)
        assert_equals(self.processor.main_registers['e'], 0xff)
        assert_equals(self.processor.main_registers['b'], 0x00)
        assert_equals(self.processor.main_registers['c'], 0x00)

        assert_equals(self.processor.condition('h'), False)
        assert_equals(self.processor.condition('p'), False)
        assert_equals(self.processor.condition('n'), False)

    def test_lddr_with_bc_equal_to_zero(self):
        # given
        self.given_register_pair_contains_value('hl', 0x1000)
        self.given_register_pair_contains_value('de', 0x2000)
        self.given_register_pair_contains_value('bc', 0x0000)

        self.memory.poke(0x1000, 0xff)

        self.given_next_instruction_is(0xed, 0xb8)

        # when
        self.processor.execute()

        # then
        self.assert_pc_address(0x0000)
        assert_equals(self.memory.peek(0x2000), 0xff)
        assert_equals(self.processor.main_registers['h'], 0x0f)
        assert_equals(self.processor.main_registers['l'], 0xff)
        assert_equals(self.processor.main_registers['d'], 0x1f)
        assert_equals(self.processor.main_registers['e'], 0xff)
        assert_equals(self.processor.main_registers['b'], 0xff)
        assert_equals(self.processor.main_registers['c'], 0xff)

        assert_equals(self.processor.condition('h'), False)
        assert_equals(self.processor.condition('p'), False)
        assert_equals(self.processor.condition('n'), False)
