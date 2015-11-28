from nose.tools import assert_equals

from tests.processor.processor_tests import TestHelper, random_byte
from z80.funcs import twos_complement, big_endian_value

__author__ = 'alan'


class Test8BitLoadGroup(TestHelper):
    def test_ld_reg_reg(self):
        operations = [
            (0x7f, 'a', 'a'), (0x78, 'a', 'b'), (0x79, 'a', 'c'), (0x7a, 'a', 'd'), (0x7b, 'a', 'e'), (0x7c, 'a', 'h'),
            (0x7d, 'a', 'l'),

            (0x47, 'b', 'a'), (0x40, 'b', 'b'), (0x41, 'b', 'c'), (0x42, 'b', 'd'), (0x43, 'b', 'e'), (0x44, 'b', 'h'),
            (0x45, 'b', 'l'),

            (0x4f, 'c', 'a'), (0x48, 'c', 'b'), (0x49, 'c', 'c'), (0x4a, 'c', 'd'), (0x4b, 'c', 'e'), (0x4c, 'c', 'h'),
            (0x4d, 'c', 'l'),

            (0x57, 'd', 'a'), (0x50, 'd', 'b'), (0x51, 'd', 'c'), (0x52, 'd', 'd'), (0x53, 'd', 'e'), (0x54, 'd', 'h'),
            (0x55, 'd', 'l'),

            (0x5f, 'e', 'a'), (0x58, 'e', 'b'), (0x59, 'e', 'c'), (0x5a, 'e', 'd'), (0x5b, 'e', 'e'), (0x5c, 'e', 'h'),
            (0x5d, 'e', 'l'),

            (0x67, 'h', 'a'), (0x60, 'h', 'b'), (0x61, 'h', 'c'), (0x62, 'h', 'd'), (0x63, 'h', 'e'), (0x64, 'h', 'h'),
            (0x65, 'h', 'l'),

            (0x6f, 'l', 'a'), (0x68, 'l', 'b'), (0x69, 'l', 'c'), (0x6a, 'l', 'd'), (0x6b, 'l', 'e'), (0x6c, 'l', 'h'),
            (0x6d, 'l', 'l')
        ]

        for (op_code, destination, source) in operations:
            yield self.check_ld_reg_reg, op_code, destination, source

    def check_ld_reg_reg(self, op_code, destination, source):
        # given
        self.given_register_contains_value(source, 0xff)
        self.given_next_instruction_is(op_code)

        # when
        self.processor.execute()

        # then
        self.assert_cycles_taken(1)
        self.assert_pc_address(0x0001)
        assert_equals(0xff, self.processor.main_registers[destination])
        assert_equals(0xff, self.processor.main_registers[source])

    def test_ld_reg_reg_indirect(self):
        operations = [
            (0x7e, 'a', 'hl'), (0x0a, 'a', 'bc'), (0x1a, 'a', 'de'),
            (0x46, 'b', 'hl'), (0x4e, 'c', 'hl'), (0x56, 'd', 'hl'), (0x5e, 'e', 'hl'), (0x66, 'h', 'hl'),
            (0x6e, 'l', 'hl')
        ]

        for (op_code, destination, source_pointer) in operations:
            yield self.check_ld_reg_reg_indirect, op_code, destination, source_pointer

    def check_ld_reg_reg_indirect(self, op_code, destination, source_pointer):
        # given
        self.given_register_pair_contains_value(source_pointer, 0xa0a0)
        self.given_next_instruction_is(op_code)
        self.memory.poke(0xa0a0, 0xaa)

        # when
        self.processor.execute()

        # then
        self.assert_cycles_taken(1)
        self.assert_pc_address(0x0001)
        assert_equals(0xaa, self.processor.main_registers[destination])

    def test_ld_reg_indirect_reg(self):
        operations = [
            (0x77, 'hl', 'a'), (0x70, 'hl', 'b'), (0x71, 'hl', 'c'), (0x72, 'hl', 'd'), (0x73, 'hl', 'e'),
            (0x02, 'bc', 'a'),
            (0x12, 'de', 'a')
        ]

        for (op_code, destination_pointer, source_register) in operations:
            yield self.check_ld_reg_indirect_reg, op_code, destination_pointer, source_register

    def check_ld_reg_indirect_reg(self, op_code, destination_pointer, source_register):
        # given
        self.given_register_contains_value(source_register, 0xbb)
        self.given_register_pair_contains_value(destination_pointer, 0xb0c0)

        self.given_next_instruction_is(op_code)

        # when
        self.processor.execute()

        # then
        self.assert_cycles_taken(1)
        self.assert_pc_address(0x0001)

        assert_equals(0xbb, self.memory.peek(0xb0c0))

    def test_ld_reg_indirect_reg_where_l_reg_is_used(self):
        # given
        self.given_register_pair_contains_value('hl', 0xb0c0)

        self.given_next_instruction_is(0x75)

        # when
        self.processor.execute()

        # then
        self.assert_cycles_taken(1)
        self.assert_pc_address(0x0001)

        assert_equals(0xc0, self.memory.peek(0xb0c0))

    def test_ld_reg_indirect_reg_where_h_reg_is_used(self):
        # given
        self.given_register_pair_contains_value('hl', 0xb0c0)

        self.given_next_instruction_is(0x74)

        # when
        self.processor.execute()

        # then
        self.assert_cycles_taken(1)
        self.assert_pc_address(0x0001)

        assert_equals(0xb0, self.memory.peek(0xb0c0))

    def test_ld_a_i(self):
        # given
        self.processor.special_registers['i'] = 0xff
        self.given_next_instruction_is(0xed, 0x57)

        # when
        self.processor.execute()

        # then
        self.assert_cycles_taken(1)
        self.assert_pc_address(0x0002)

        assert_equals(0xff, self.processor.main_registers['a'])

    def test_ld_reg_immediate(self):
        operations = [
            (0x3e, 'a', 0x10), (0x06, 'b', 0x11), (0x0e, 'c', 0x22), (0x16, 'd', 0x33), (0x1e, 'e', 0xaa),
            (0x26, 'h', 0xab), (0x2e, 'l', 0xef)
        ]

        for (op_code, destination_register, operand) in operations:
            yield self.check_ld_reg_immediate, op_code, destination_register, operand

    def check_ld_reg_immediate(self, op_code, destination_register, operand):
        # given
        self.given_next_instruction_is(op_code, operand)

        # when
        self.processor.execute()

        # then
        self.assert_cycles_taken(1)
        self.assert_pc_address(0x0002)

        assert_equals(operand, self.processor.main_registers[destination_register])

    def test_ld_reg_indirect_immediate(self):
        # given
        self.given_next_instruction_is(0x36, 0xff)
        self.given_register_pair_contains_value('hl', 0xa123)

        # when
        self.processor.execute()

        # then
        self.assert_cycles_taken(1)
        self.assert_pc_address(0x0002)

        assert_equals(0xff, self.memory.peek(0xa123))

    def test_ld_reg_indexed_addr(self):
        operations = [
            ([0xdd, 0x7e], 'a', 'ix'), ([0xfd, 0x7e], 'a', 'iy'),
            ([0xdd, 0x46], 'b', 'ix'), ([0xfd, 0x46], 'b', 'iy'),
            ([0xdd, 0x4e], 'c', 'ix'), ([0xfd, 0x4e], 'c', 'iy'),
            ([0xdd, 0x56], 'd', 'ix'), ([0xfd, 0x56], 'd', 'iy'),
            ([0xdd, 0x5e], 'e', 'ix'), ([0xfd, 0x5e], 'e', 'iy'),
            ([0xdd, 0x66], 'h', 'ix'), ([0xfd, 0x66], 'h', 'iy'),
            ([0xdd, 0x6e], 'l', 'ix'), ([0xfd, 0x6e], 'l', 'iy')
        ]

        for op_codes, destination_register, index_register in operations:
            yield self.check_ld_reg_indexed_addr, op_codes, destination_register, index_register, random_byte()

    def check_ld_reg_indexed_addr(self, op_codes, destination_register, index_register, operand):
        # given
        self.given_next_instruction_is(op_codes[0], op_codes[1], operand)
        self.given_register_contains_value(index_register, 0x1000)

        referenced_address = 0x1000 + twos_complement(operand)
        address_value = random_byte()
        self.memory.poke(referenced_address, address_value)

        # when
        self.processor.execute()

        # then
        self.assert_cycles_taken(1)
        self.assert_pc_address(0x0003)

        assert_equals(self.processor.main_registers[destination_register], address_value)

    def test_ld_reg_indexed_addr_offset_wraparound_low(self):
        # given
        self.given_next_instruction_is(0xdd, 0x7e, 0x80)
        self.given_register_contains_value('ix', 0x0a)

        self.memory.poke(0xff8a, 0x12)

        # when
        self.processor.execute()

        # then
        self.assert_cycles_taken(1)
        self.assert_pc_address(0x0003)

        assert_equals(self.processor.main_registers['a'], 0x12)

    def test_ld_reg_indexed_addr_offset_wraparound_high(self):
        # given
        self.given_next_instruction_is(0xdd, 0x7e, 0x7f)
        self.given_register_contains_value('ix', 0xffff)

        self.memory.poke(0x007e, 0x12)

        # when
        self.processor.execute()

        # then
        assert_equals(self.processor.special_registers['pc'], 0x0003)
        assert_equals(self.processor.main_registers['a'], 0x12)

    def test_ld_a_ext_addr(self):
        # given
        little_endian_address = [random_byte(), random_byte()]
        self.given_next_instruction_is(0x3a, little_endian_address[0], little_endian_address[1])

        memory_value = random_byte()
        self.memory.poke(big_endian_value(little_endian_address), memory_value)

        # when
        self.processor.execute()

        # then
        self.assert_cycles_taken(1)
        self.assert_pc_address(0x0003)

        assert_equals(self.processor.main_registers['a'], memory_value)

    def test_ld_indexed_reg_from_reg(self):
        operations = [
            ([0xdd, 0x77], 'ix', 'a'),
            ([0xfd, 0x77], 'iy', 'a'),
            ([0xdd, 0x70], 'ix', 'b'),
            ([0xfd, 0x70], 'iy', 'b'),
            ([0xdd, 0x71], 'ix', 'c'),
            ([0xfd, 0x71], 'iy', 'c'),
            ([0xdd, 0x72], 'ix', 'd'),
            ([0xfd, 0x72], 'iy', 'd'),
            ([0xdd, 0x73], 'ix', 'e'),
            ([0xfd, 0x73], 'iy', 'e'),
            ([0xdd, 0x74], 'ix', 'h'),
            ([0xfd, 0x74], 'iy', 'h'),
            ([0xdd, 0x75], 'ix', 'l'),
            ([0xfd, 0x75], 'iy', 'l')
        ]

        for op_codes, destination_index_register, source_register in operations:
            yield self.check_ld_indexed_reg_from_reg, op_codes, destination_index_register, \
                  source_register, random_byte()

    def check_ld_indexed_reg_from_reg(self, op_codes, destination_index_register, source_register, operand):
        # given
        self.given_next_instruction_is(op_codes[0], op_codes[1], operand)

        register_value = random_byte()
        self.given_register_contains_value(source_register, register_value)

        self.given_register_contains_value(destination_index_register, 0x1000)

        # when
        self.processor.execute()

        # then
        self.assert_cycles_taken(1)
        self.assert_pc_address(0x0003)

        referenced_address = 0x1000 + twos_complement(operand)
        assert_equals(self.memory.peek(referenced_address), register_value)

    def test_ld_ext_addr_from_a(self):
        # given
        register_value = random_byte()
        self.given_register_contains_value('a', register_value)

        little_endian_address = [random_byte(), random_byte()]
        self.given_next_instruction_is(0x32, little_endian_address[0], little_endian_address[1])

        # when
        self.processor.execute()

        # then
        self.assert_cycles_taken(1)
        self.assert_pc_address(0x0003)

        assert_equals(self.memory.peek(big_endian_value(little_endian_address)), register_value)

    def test_ld_indexed_addr_immediate(self):
        operations = [
            ([0xdd, 0x36], 'ix'),
            ([0xfd, 0x36], 'iy')
        ]

        for op_codes, index_register in operations:
            yield self.check_ld_indexed_addr_immediate, op_codes, index_register

    def check_ld_indexed_addr_immediate(self, op_codes, index_register):
        # given
        operand = random_byte()
        immediate_value = random_byte()

        self.processor.index_registers[index_register] = 0x1000
        self.given_next_instruction_is(op_codes[0], op_codes[1], operand, immediate_value)

        # when
        self.processor.execute()

        # then
        assert_equals(self.memory.peek(0x1000 + twos_complement(operand)), immediate_value)