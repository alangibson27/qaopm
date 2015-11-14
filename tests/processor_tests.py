from nose.tools import *
from random import randint
from z80.funcs import big_endian_value, twos_complement
from z80.memory import Memory
from z80.processor import Processor


def random_byte():
    return randint(0x00, 0xff)


class TestHelper:
    def __init__(self):
        self.instruction_pointer = 0x0
        self.memory = Memory()
        self.processor = Processor(self.memory)

    def given_next_instruction_is(self, *args):
        for arg in args:
            self.memory.poke(self.instruction_pointer, arg)
            self.instruction_pointer += 1

    def given_register_contains_value(self, register, value):
        if register == 'ix' or register == 'iy':
            self.processor.index_registers[register] = value
        else:
            self.processor.main_registers[register] = value

    def given_register_pair_contains_value(self, register_pair, value):
        self.processor.main_registers[register_pair[0]] = value >> 8
        self.processor.main_registers[register_pair[1]] = value & 0xff

    def given_stack_pointer_is(self, address):
        self.processor.special_registers['sp'] = address

    def given_program_counter_is(self, address):
        self.processor.special_registers['pc'] = address
        self.instruction_pointer = address

class Test8BitLoadGroup(TestHelper):
    def test_ld_reg_reg(self):
        operations = [
            (0x7f, 'a', 'a'), (0x78, 'a', 'b'), (0x79, 'a', 'c'), (0x7a, 'a', 'd'), (0x7b, 'a', 'e'), (0x7c, 'a', 'h'), (0x7d, 'a', 'l'),
            (0x47, 'b', 'a'), (0x40, 'b', 'b'), (0x41, 'b', 'c'), (0x42, 'b', 'd'), (0x43, 'b', 'e'), (0x44, 'b', 'h'), (0x45, 'b', 'l'),
            (0x4f, 'c', 'a'), (0x48, 'c', 'b'), (0x49, 'c', 'c'), (0x4a, 'c', 'd'), (0x4b, 'c', 'e'), (0x4c, 'c', 'h'), (0x4d, 'c', 'l'),
            (0x57, 'd', 'a'), (0x50, 'd', 'b'), (0x51, 'd', 'c'), (0x52, 'd', 'd'), (0x53, 'd', 'e'), (0x54, 'd', 'h'), (0x55, 'd', 'l'),
            (0x5f, 'e', 'a'), (0x58, 'e', 'b'), (0x59, 'e', 'c'), (0x5a, 'e', 'd'), (0x5b, 'e', 'e'), (0x5c, 'e', 'h'), (0x5d, 'e', 'l'),
            (0x67, 'h', 'a'), (0x60, 'h', 'b'), (0x61, 'h', 'c'), (0x62, 'h', 'd'), (0x63, 'h', 'e'), (0x64, 'h', 'h'), (0x65, 'h', 'l'),
            (0x6f, 'l', 'a'), (0x68, 'l', 'b'), (0x69, 'l', 'c'), (0x6a, 'l', 'd'), (0x6b, 'l', 'e'), (0x6c, 'l', 'h'), (0x6d, 'l', 'l')
        ]

        for (op_code, destination, source) in operations:
            yield self.check_ld_reg_reg, op_code, destination, source

    def check_ld_reg_reg(self, op_code, destination, source):
        # given
        self.given_register_contains_value(source, 0xff)
        self.given_next_instruction_is(op_code)

        # when
        self.processor.single_cycle()

        # then
        assert_equals(0x0001, self.processor.special_registers['pc'])
        assert_equals(0xff, self.processor.main_registers[destination])
        assert_equals(0xff, self.processor.main_registers[source])

    def test_ld_reg_reg_indirect(self):
        operations = [
            (0x7e, 'a', 'hl'), (0x0a, 'a', 'bc'), (0x1a, 'a', 'de'),
            (0x46, 'b', 'hl'), (0x4e, 'c', 'hl'), (0x56, 'd', 'hl'), (0x5e, 'e', 'hl'), (0x66, 'h', 'hl'), (0x6e, 'l', 'hl')
        ]

        for (op_code, destination, source_pointer) in operations:
            yield self.check_ld_reg_reg_indirect, op_code, destination, source_pointer

    def check_ld_reg_reg_indirect(self, op_code, destination, source_pointer):
        # given
        self.given_register_pair_contains_value(source_pointer, 0xa0a0)
        self.given_next_instruction_is(op_code)
        self.memory.poke(0xa0a0, 0xaa)

        # when
        self.processor.single_cycle()

        # then
        assert_equals(0x0001, self.processor.special_registers['pc'])
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
        self.processor.single_cycle()

        # then
        assert_equals(0x0001, self.processor.special_registers['pc'])
        assert_equals(0xbb, self.memory.peek(0xb0c0))

    def test_ld_reg_indirect_reg_where_l_reg_is_used(self):
        # given
        self.given_register_pair_contains_value('hl', 0xb0c0)

        self.given_next_instruction_is(0x75)

        # when
        self.processor.single_cycle()

        # then
        assert_equals(0x0001, self.processor.special_registers['pc'])
        assert_equals(0xc0, self.memory.peek(0xb0c0))

    def test_ld_reg_indirect_reg_where_h_reg_is_used(self):
        # given
        self.given_register_pair_contains_value('hl', 0xb0c0)

        self.given_next_instruction_is(0x74)

        # when
        self.processor.single_cycle()

        # then
        assert_equals(0x0001, self.processor.special_registers['pc'])
        assert_equals(0xb0, self.memory.peek(0xb0c0))

    def test_ld_a_i(self):
        # given
        self.processor.special_registers['i'] = 0xff
        self.given_next_instruction_is(0xed, 0x57)

        # when
        self.processor.single_cycle()

        # then
        assert_equals(0x0002, self.processor.special_registers['pc'])
        assert_equals(0xff, self.processor.main_registers['a'])

    def test_ld_reg_immediate(self):
        operations = [
            (0x3e, 'a', 0x10), (0x06, 'b', 0x11), (0x0e, 'c', 0x22), (0x16, 'd', 0x33), (0x1e, 'e', 0xaa), (0x26, 'h', 0xab), (0x2e, 'l', 0xef)
        ]

        for (op_code, destination_register, operand) in operations:
            yield self.check_ld_reg_immediate, op_code, destination_register, operand

    def check_ld_reg_immediate(self, op_code, destination_register, operand):
        # given
        self.given_next_instruction_is(op_code, operand)

        # when
        self.processor.single_cycle()

        # then
        assert_equals(0x0002, self.processor.special_registers['pc'])
        assert_equals(operand, self.processor.main_registers[destination_register])

    def test_ld_reg_indirect_immediate(self):
        # given
        self.given_next_instruction_is(0x36, 0xff)
        self.given_register_pair_contains_value('hl', 0xa123)

        # when
        self.processor.single_cycle()

        # then
        assert_equals(0x0002, self.processor.special_registers['pc'])
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
        self.processor.single_cycle()

        # then
        assert_equals(self.processor.special_registers['pc'], 0x0003)
        assert_equals(self.processor.main_registers[destination_register], address_value)

    def test_ld_reg_indexed_addr_offset_wraparound_low(self):
        # given
        self.given_next_instruction_is(0xdd, 0x7e, 0x80)
        self.given_register_contains_value('ix', 0x0a)

        self.memory.poke(0xff8a, 0x12)

        # when
        self.processor.single_cycle()

        # then
        assert_equals(self.processor.special_registers['pc'], 0x0003)
        assert_equals(self.processor.main_registers['a'], 0x12)

    def test_ld_reg_indexed_addr_offset_wraparound_high(self):
        # given
        self.given_next_instruction_is(0xdd, 0x7e, 0x7f)
        self.given_register_contains_value('ix', 0xffff)

        self.memory.poke(0x007e, 0x12)

        # when
        self.processor.single_cycle()

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
        self.processor.single_cycle()

        # then
        assert_equals(self.processor.special_registers['pc'], 0x0003)
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
            yield self.check_ld_indexed_reg_from_reg, op_codes, destination_index_register, source_register, random_byte()

    def check_ld_indexed_reg_from_reg(self, op_codes, destination_index_register, source_register, operand):
        # given
        self.given_next_instruction_is(op_codes[0], op_codes[1], operand)

        register_value = random_byte()
        self.given_register_contains_value(source_register, register_value)

        self.given_register_contains_value(destination_index_register, 0x1000)

        # when
        self.processor.single_cycle()

        # then
        assert_equals(self.processor.special_registers['pc'], 0x0003)

        referenced_address = 0x1000 + twos_complement(operand)
        assert_equals(self.memory.peek(referenced_address), register_value)

    def test_ld_ext_addr_from_a(self):
        # given
        register_value = random_byte()
        self.given_register_contains_value('a', register_value)

        little_endian_address = [random_byte(), random_byte()]
        self.given_next_instruction_is(0x32, little_endian_address[0], little_endian_address[1])

        # when
        self.processor.single_cycle()

        # then
        assert_equals(self.processor.special_registers['pc'], 0x0003)
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
        self.processor.single_cycle()

        # then
        assert_equals(self.memory.peek(0x1000 + twos_complement(operand)), immediate_value)


class Test16BitLoadGroup(TestHelper):
    def test_ld_16reg_16reg(self):
        operations = [([0xf9], 'hl'), ([0xdd, 0xf9], 'ix'), ([0xfd, 0xf9], 'iy')]
        for op_codes, register_pair in operations:
            yield self.check_ld_16reg_16reg, op_codes, register_pair

    def check_ld_16reg_16reg(self, op_codes, register_pair):
        # given
        if register_pair == 'ix' or register_pair == 'iy':
            self.processor.index_registers[register_pair] = 0xbeef
        else:
            self.given_register_pair_contains_value(register_pair, 0xbeef)

        if len(op_codes) == 1:
            self.given_next_instruction_is(op_codes[0])
        else:
            self.given_next_instruction_is(op_codes[0], op_codes[1])

        # when
        self.processor.single_cycle()

        # then
        assert_equals(self.processor.special_registers['sp'], 0xbeef)

    def test_ld_16reg_immediate(self):
        operations = [
            ([0x01], 'bc'),
            ([0x11], 'de'),
            ([0x21], 'hl'),
            ([0x31], 'sp'),
            ([0xdd, 0x21], 'ix'),
            ([0xfd, 0x21], 'iy')
        ]

        for op_codes, register_pair in operations:
            yield self.check_ld_16reg_immediate, op_codes, register_pair

    def check_ld_16reg_immediate(self, op_codes, register_pair):
        # given
        little_endian_address = [random_byte(), random_byte()]
        if len(op_codes) == 1:
            self.given_next_instruction_is(op_codes[0], little_endian_address[0], little_endian_address[1])
        else:
            self.given_next_instruction_is(op_codes[0], op_codes[1], little_endian_address[0], little_endian_address[1])

        # when
        self.processor.single_cycle()

        # then
        if register_pair == 'ix':
            assert_equals(self.processor.index_registers['ix'], big_endian_value(little_endian_address))
        elif register_pair == 'iy':
            assert_equals(self.processor.index_registers['iy'], big_endian_value(little_endian_address))
        elif register_pair == 'sp':
            assert_equals(self.processor.special_registers['sp'], big_endian_value(little_endian_address))
        else:
            assert_equals(self.processor.main_registers[register_pair[0]], little_endian_address[1])
            assert_equals(self.processor.main_registers[register_pair[1]], little_endian_address[0])

    def test_push_without_wraparound(self):
        operations = [
            ([0xf6], 'af'),
            ([0xc6], 'bc'),
            ([0xd6], 'de'),
            ([0xe6], 'hl'),
            ([0xdd, 0xe6], 'ix'),
            ([0xfd, 0xe6], 'iy')
        ]

        for op_codes, register_pair in operations:
            yield self.check_push_without_wraparound, op_codes, register_pair

    def check_push_without_wraparound(self, op_codes, register_pair):
        lsb = random_byte()
        msb = random_byte()

        # given
        if register_pair == 'ix' or register_pair == 'iy':
            self.given_register_contains_value(register_pair, big_endian_value([lsb, msb]))
        else:
            self.given_register_contains_value(register_pair[0], msb)
            self.given_register_contains_value(register_pair[1], lsb)

        self.given_stack_pointer_is(0xffff)

        if len(op_codes) == 1:
            self.given_next_instruction_is(op_codes[0])
        else:
            self.given_next_instruction_is(op_codes[0], op_codes[1])

        # when
        self.processor.single_cycle()

        # then
        assert_equals(self.processor.special_registers['sp'], 0xfffd)
        assert_equals(self.memory.peek(0xfffe), msb)
        assert_equals(self.memory.peek(0xfffd), lsb)

    def test_push_with_wraparound(self):
        # given
        self.given_stack_pointer_is(0x0000)
        self.given_register_pair_contains_value('hl', 0xabcd)

        self.given_next_instruction_is(0xe6)

        # when
        self.processor.single_cycle()

        # then
        assert_equals(self.memory.peek(0xffff), 0xab)
        assert_equals(self.memory.peek(0xfffe), 0xcd)

    def test_pop_without_wraparound(self):
        operations = [
            ([0xf1], 'af'), ([0xc1], 'bc'), ([0xd1], 'de'), ([0xe1], 'hl'), ([0xdd, 0xe1], 'ix'), ([0xfd, 0xe1], 'iy')
        ]

        for op_codes, register_pair in operations:
            yield self.check_pop_without_workaround, op_codes, register_pair

    def check_pop_without_workaround(self, op_codes, register_pair):
        # given
        msb = random_byte()
        lsb = random_byte()

        self.memory.poke(0xfff0, lsb)
        self.memory.poke(0xfff1, msb)

        self.given_stack_pointer_is(0xfff0)

        if len(op_codes) == 1:
            self.given_next_instruction_is(op_codes[0])
        else:
            self.given_next_instruction_is(op_codes[0], op_codes[1])

        # when
        self.processor.single_cycle()

        # then
        assert_equals(self.processor.special_registers['sp'], 0xfff2)

        if register_pair == 'ix' or register_pair == 'iy':
            assert_equals(self.processor.index_registers[register_pair], big_endian_value([lsb, msb]))
        else:
            assert_equals(self.processor.main_registers[register_pair[0]], msb)
            assert_equals(self.processor.main_registers[register_pair[1]], lsb)

    def test_pop_with_wraparound(self):
        # given
        self.memory.poke(0xffff, 0xab)
        self.memory.poke(0x0000, 0xcd)

        self.given_stack_pointer_is(0xffff)

        self.given_program_counter_is(0x1000)
        self.given_next_instruction_is(0xe1)

        # when
        self.processor.single_cycle()

        # then
        assert_equals(self.processor.main_registers['h'], 0xcd)
        assert_equals(self.processor.main_registers['l'], 0xab)
        assert_equals(self.processor.special_registers['sp'], 0x0001)

    def test_ld_ext_addr_16reg(self):
        operations = [
            ([0x22], 'hl'),
            ([0xed, 0x43], 'bc'),
            ([0xed, 0x53], 'de'),
            ([0xed, 0x63], 'hl'),
            ([0xed, 0x73], 'sp'),
            ([0xdd, 0x22], 'ix'),
            ([0xfd, 0x22], 'iy')
        ]

        for op_codes, dest_register_pair in operations:
            yield self.check_ld_ext_addr_16reg, op_codes, dest_register_pair

    def check_ld_ext_addr_16reg(self, op_codes, dest_register_pair):
        # given
        if dest_register_pair == 'ix' or dest_register_pair == 'iy':
            self.processor.index_registers[dest_register_pair] = 0x1234
        elif dest_register_pair == 'sp':
            self.processor.special_registers[dest_register_pair] = 0x1234
        else:
            self.processor.main_registers[dest_register_pair[0]] = 0x12
            self.processor.main_registers[dest_register_pair[1]] = 0x34

        if len(op_codes) == 1:
            self.given_next_instruction_is(op_codes[0], 0xee, 0xbe)
        else:
            self.given_next_instruction_is(op_codes[0], op_codes[1], 0xee, 0xbe)

        # when
        self.processor.single_cycle()

        # then
        assert_equals(self.memory.peek(0xbeee), 0x34)
        assert_equals(self.memory.peek(0xbeef), 0x12)

    def test_ld_16reg_ext_addr_without_wraparound(self):
        operations = [
            ([0xed, 0x4b], 'bc'),
            ([0xed, 0x5b], 'de'),
            ([0x2a], 'hl'),
            ([0xed, 0x6b], 'hl'),
            ([0xed, 0x7b], 'sp'),
            ([0xdd, 0x2a], 'ix'),
            ([0xfd, 0x2a], 'iy')
        ]

        for op_codes, dest_register in operations:
            yield self.check_ld_16reg_ext_addr_without_wraparound, op_codes, dest_register

    def check_ld_16reg_ext_addr_without_wraparound(self, op_codes, dest_register):
        # given
        self.memory.poke(0x1000, 0x10)
        self.memory.poke(0x1001, 0x20)

        if len(op_codes) == 1:
            self.given_next_instruction_is(op_codes[0], 0x00, 0x10)
        else:
            self.given_next_instruction_is(op_codes[0], op_codes[1], 0x00, 0x10)

        # when
        self.processor.single_cycle()

        # then
        if dest_register == 'ix' or dest_register == 'iy':
            assert_equals(self.processor.index_registers[dest_register], 0x2010)
        elif dest_register == 'sp':
            assert_equals(self.processor.special_registers['sp'], 0x2010)
        else:
            assert_equals(self.processor.main_registers[dest_register[0]], 0x20)
            assert_equals(self.processor.main_registers[dest_register[1]], 0x10)