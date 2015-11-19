from funcs import big_endian_value, twos_complement

class Op:
    def __init__(self, function, mnemonic):
        self.function = function
        self.mnemonic = mnemonic

class Processor:
    def __init__(self, memory):
        self.memory = memory
        self.main_registers = self.build_swappable_register_set()
        self.alternate_registers = self.build_swappable_register_set()
        self.special_registers = self.build_special_register_set()
        self.index_registers = self.build_index_register_set()
        self.operations_by_opcode = self.init_opcode_map()
        self.condition_masks = {
            'c': 0b00000001,
            'n': 0b00000010,
            'p': 0b00000100,
            'h': 0b00010000,
            'z': 0b01000000,
            's': 0b10000000
        }

    def build_swappable_register_set(self):
        return {'a': 0x0, 'f': 0x0, 'b': 0x0, 'c': 0x0, 'd': 0x0, 'e': 0x0, 'h': 0x0, 'l': 0x0}

    def build_index_register_set(self):
        return {'ix': 0x0000, 'iy': 0x0000}

    def build_special_register_set(self):
        return {'i': 0x0, 'r': 0x0, 'sp': 0xffff, 'pc': 0x0000}

    def create_ld_reg_from_reg(self, destination, source):
        return Op(lambda: self.ld_reg_from_reg(destination, source), 'ld {}, {}'.format(destination, source))

    def create_ld_reg_from_reg_indirect(self, destination, source_register):
        return Op(lambda: self.ld_reg_from_reg_indirect(destination, source_register), 'ld {}, ({})'.format(destination, source_register))

    def create_ld_reg_indirect_from_reg(self, destination_register, source_register):
        return Op(lambda: self.ld_reg_indirect_from_reg(destination_register, source_register), 'ld ({}), {}'.format(destination_register, source_register))

    def init_opcode_map(self):
        return {
            0x01: Op(lambda: self.ld_16reg_immediate('bc'), 'ld bc, nn'),
            0x02: self.create_ld_reg_indirect_from_reg('bc', 'a'),
            0x06: Op(lambda: self.ld_reg_immediate('b'), 'ld b, n'),
            0x08: Op(self.ex_af_alt_af, "ex af, af'"),
            0x0a: self.create_ld_reg_from_reg_indirect('a', 'bc'),
            0x0e: Op(lambda: self.ld_reg_immediate('c'), 'ld c, n'),

            0x11: Op(lambda: self.ld_16reg_immediate('de'), 'ld de, nn'),
            0x12: self.create_ld_reg_indirect_from_reg('de', 'a'),
            0x16: Op(lambda: self.ld_reg_immediate('d'), 'ld d, n'),
            0x1a: self.create_ld_reg_from_reg_indirect('a', 'de'),
            0x1e: Op(lambda: self.ld_reg_immediate('e'), 'ld e, n'),

            0x21: Op(lambda: self.ld_16reg_immediate('hl'), 'ld hl, nn'),
            0x22: Op(lambda: self.ld_ext_16reg('hl'), 'ld (nn), hl'),
            0x26: Op(lambda: self.ld_reg_immediate('h'), 'ld h, n'),
            0x2a: Op(lambda: self.ld_16reg_ext('hl'), 'ld hl, (nn)'),
            0x2e: Op(lambda: self.ld_reg_immediate('l'), 'ld l, n'),

            0x31: Op(lambda: self.ld_sp_immediate(), 'ld sp, nn'),
            0x32: Op(self.ld_ext_addr_a, 'ld (nn), a'),
            0x36: Op(lambda: self.ld_hl_indirect_immediate(), 'ld (hl), n'),
            0x3a: Op(self.ld_a_ext_addr, 'ld a, (nn)'),
            0x3e: Op(lambda: self.ld_reg_immediate('a'), 'ld a, n'),

            0x40: self.create_ld_reg_from_reg('b', 'b'),
            0x41: self.create_ld_reg_from_reg('b', 'c'),
            0x42: self.create_ld_reg_from_reg('b', 'd'),
            0x43: self.create_ld_reg_from_reg('b', 'e'),
            0x44: self.create_ld_reg_from_reg('b', 'h'),
            0x45: self.create_ld_reg_from_reg('b', 'l'),
            0x46: self.create_ld_reg_from_reg_indirect('b', 'hl'),
            0x47: self.create_ld_reg_from_reg('b', 'a'),

            0x48: self.create_ld_reg_from_reg('c', 'b'),
            0x49: self.create_ld_reg_from_reg('c', 'c'),
            0x4a: self.create_ld_reg_from_reg('c', 'd'),
            0x4b: self.create_ld_reg_from_reg('c', 'e'),
            0x4c: self.create_ld_reg_from_reg('c', 'h'),
            0x4d: self.create_ld_reg_from_reg('c', 'l'),
            0x4e: self.create_ld_reg_from_reg_indirect('c', 'hl'),
            0x4f: self.create_ld_reg_from_reg('c', 'a'),

            0x50: self.create_ld_reg_from_reg('d', 'b'),
            0x51: self.create_ld_reg_from_reg('d', 'c'),
            0x52: self.create_ld_reg_from_reg('d', 'd'),
            0x53: self.create_ld_reg_from_reg('d', 'e'),
            0x54: self.create_ld_reg_from_reg('d', 'h'),
            0x55: self.create_ld_reg_from_reg('d', 'l'),
            0x56: self.create_ld_reg_from_reg_indirect('d', 'hl'),
            0x57: self.create_ld_reg_from_reg('d', 'a'),

            0x58: self.create_ld_reg_from_reg('e', 'b'),
            0x59: self.create_ld_reg_from_reg('e', 'c'),
            0x5a: self.create_ld_reg_from_reg('e', 'd'),
            0x5b: self.create_ld_reg_from_reg('e', 'e'),
            0x5c: self.create_ld_reg_from_reg('e', 'h'),
            0x5d: self.create_ld_reg_from_reg('e', 'l'),
            0x5e: self.create_ld_reg_from_reg_indirect('e', 'hl'),
            0x5f: self.create_ld_reg_from_reg('e', 'a'),

            0x60: self.create_ld_reg_from_reg('h', 'b'),
            0x61: self.create_ld_reg_from_reg('h', 'c'),
            0x62: self.create_ld_reg_from_reg('h', 'd'),
            0x63: self.create_ld_reg_from_reg('h', 'e'),
            0x64: self.create_ld_reg_from_reg('h', 'h'),
            0x65: self.create_ld_reg_from_reg('h', 'l'),
            0x66: self.create_ld_reg_from_reg_indirect('h', 'hl'),
            0x67: self.create_ld_reg_from_reg('h', 'a'),

            0x68: self.create_ld_reg_from_reg('l', 'b'),
            0x69: self.create_ld_reg_from_reg('l', 'c'),
            0x6a: self.create_ld_reg_from_reg('l', 'd'),
            0x6b: self.create_ld_reg_from_reg('l', 'e'),
            0x6c: self.create_ld_reg_from_reg('l', 'h'),
            0x6d: self.create_ld_reg_from_reg('l', 'l'),
            0x6e: self.create_ld_reg_from_reg_indirect('l', 'hl'),
            0x6f: self.create_ld_reg_from_reg('l', 'a'),

            0x70: self.create_ld_reg_indirect_from_reg('hl', 'b'),
            0x71: self.create_ld_reg_indirect_from_reg('hl', 'c'),
            0x72: self.create_ld_reg_indirect_from_reg('hl', 'd'),
            0x73: self.create_ld_reg_indirect_from_reg('hl', 'e'),
            0x74: self.create_ld_reg_indirect_from_reg('hl', 'h'),
            0x75: self.create_ld_reg_indirect_from_reg('hl', 'l'),
            0x77: self.create_ld_reg_indirect_from_reg('hl', 'a'),

            0x78: self.create_ld_reg_from_reg('a', 'b'),
            0x79: self.create_ld_reg_from_reg('a', 'c'),
            0x7a: self.create_ld_reg_from_reg('a', 'd'),
            0x7b: self.create_ld_reg_from_reg('a', 'e'),
            0x7c: self.create_ld_reg_from_reg('a', 'h'),
            0x7d: self.create_ld_reg_from_reg('a', 'l'),
            0x7e: self.create_ld_reg_from_reg_indirect('a', 'hl'),
            0x7f: self.create_ld_reg_from_reg('a', 'a'),

            0xc1: Op(lambda: self.pop('bc'), 'pop bc'),
            0xc6: Op(lambda: self.push('bc'), 'push bc'),

            0xd1: Op(lambda: self.pop('de'), 'pop de'),
            0xd6: Op(lambda: self.push('de'), 'push de'),
            0xd9: Op(self.exx, 'exx'),

            0xe1: Op(lambda: self.pop('hl'), 'pop hl'),
            0xe6: Op(lambda: self.push('hl'), 'push hl'),

            0xf1: Op(lambda: self.pop('af'), 'pop af'),
            0xf6: Op(lambda: self.push('af'), 'push af'),
            0xf9: Op(self.ld_sp_hl, 'ld sp, hl'),

            0xe3: Op(self.ex_sp_indirect_hl, 'ex (sp), hl'),
            0xed: self.init_ed_opcodes(),
            0xeb: Op(self.ex_de_hl, 'ex de, hl'),
            0xdd: self.init_dd_opcodes(),
            0xfd: self.init_fd_opcodes()
        }

    def init_ed_opcodes(self):
        return {
            0x43: Op(lambda: self.ld_ext_16reg('bc'), 'ld (nn), bc'),
            0x4b: Op(lambda: self.ld_16reg_ext('bc'), 'ld bc, (nn)'),

            0x53: Op(lambda: self.ld_ext_16reg('de'), 'ld (nn), de'),
            0x5b: Op(lambda: self.ld_16reg_ext('de'), 'ld de, (nn)'),

            0x63: Op(lambda: self.ld_ext_16reg('hl'), 'ld (nn), hl'),
            0x6b: Op(lambda: self.ld_16reg_ext('hl'), 'ld hl, (nn)'),

            0x73: Op(lambda: self.ld_ext_sp(), 'ld (nn), sp'),
            0x7b: Op(lambda: self.ld_sp_ext(), 'ld sp, (nn)'),

            0x57: Op(self.ld_a_i, 'ld a, i'),

            0xa0: Op(self.ldi, 'ldi')
        }

    def init_dd_opcodes(self):
        return {
            0x21: Op(lambda: self.ld_indexed_reg_immediate('ix'), 'ld ix, nn'),
            0x22: Op(lambda: self.ld_ext_indexed_16reg('ix'), 'ld (nn), ix'),
            0x2a: Op(lambda: self.ld_indexed_16reg_ext('ix'), 'ld ix, (nn)'),
            0x36: Op(lambda: self.ld_indexed_addr_immediate('ix'), 'ld (ix + d), n'),
            0x46: Op(lambda: self.ld_reg_indexed_addr('b', 'ix'), 'ld b, (ix + d)'),
            0x4e: Op(lambda: self.ld_reg_indexed_addr('c', 'ix'), 'ld c, (ix + d)'),
            0x56: Op(lambda: self.ld_reg_indexed_addr('d', 'ix'), 'ld d, (ix + d)'),
            0x5e: Op(lambda: self.ld_reg_indexed_addr('e', 'ix'), 'ld e, (ix + d)'),
            0x66: Op(lambda: self.ld_reg_indexed_addr('h', 'ix'), 'ld h, (ix + d)'),
            0x6e: Op(lambda: self.ld_reg_indexed_addr('l', 'ix'), 'ld l, (ix + d)'),
            0x70: Op(lambda: self.ld_indexed_reg_from_reg('ix', 'b'), 'ld (ix + d), b'),
            0x71: Op(lambda: self.ld_indexed_reg_from_reg('ix', 'c'), 'ld (ix + d), c'),
            0x72: Op(lambda: self.ld_indexed_reg_from_reg('ix', 'd'), 'ld (ix + d), d'),
            0x73: Op(lambda: self.ld_indexed_reg_from_reg('ix', 'e'), 'ld (ix + d), e'),
            0x74: Op(lambda: self.ld_indexed_reg_from_reg('ix', 'h'), 'ld (ix + d), h'),
            0x75: Op(lambda: self.ld_indexed_reg_from_reg('ix', 'l'), 'ld (ix + d), l'),
            0x77: Op(lambda: self.ld_indexed_reg_from_reg('ix', 'a'), 'ld (ix + d), a'),
            0x7e: Op(lambda: self.ld_reg_indexed_addr('a', 'ix'), 'ld a, (ix + d)'),

            0xe1: Op(lambda: self.pop_indexed('ix'), 'pop ix'),
            0xe3: Op(lambda: self.ex_sp_indirect_index_reg('ix'), 'ex (sp), ix'),
            0xe6: Op(lambda: self.push_indexed('ix'), 'push ix'),

            0xf9: Op(lambda: self.ld_sp_indexed_16reg('ix'), 'ld sp, ix')
        }

    def init_fd_opcodes(self):
        return {
            0x21: Op(lambda: self.ld_indexed_reg_immediate('iy'), 'ld iy, nn'),
            0x22: Op(lambda: self.ld_ext_indexed_16reg('iy'), 'ld (nn), iy'),
            0x2a: Op(lambda: self.ld_indexed_16reg_ext('iy'), 'ld iy, (nn)'),
            0x36: Op(lambda: self.ld_indexed_addr_immediate('iy'), 'ld (iy + d), n'),
            0x46: Op(lambda: self.ld_reg_indexed_addr('b', 'iy'), 'ld b, (iy + d)'),
            0x4e: Op(lambda: self.ld_reg_indexed_addr('c', 'iy'), 'ld c, (iy + d)'),
            0x56: Op(lambda: self.ld_reg_indexed_addr('d', 'iy'), 'ld d, (iy + d)'),
            0x5e: Op(lambda: self.ld_reg_indexed_addr('e', 'iy'), 'ld e, (iy + d)'),
            0x66: Op(lambda: self.ld_reg_indexed_addr('h', 'iy'), 'ld h, (iy + d)'),
            0x6e: Op(lambda: self.ld_reg_indexed_addr('l', 'iy'), 'ld l, (iy + d)'),
            0x70: Op(lambda: self.ld_indexed_reg_from_reg('iy', 'b'), 'ld (iy + d), b'),
            0x71: Op(lambda: self.ld_indexed_reg_from_reg('iy', 'c'), 'ld (iy + d), c'),
            0x72: Op(lambda: self.ld_indexed_reg_from_reg('iy', 'd'), 'ld (iy + d), d'),
            0x73: Op(lambda: self.ld_indexed_reg_from_reg('iy', 'e'), 'ld (iy + d), e'),
            0x74: Op(lambda: self.ld_indexed_reg_from_reg('iy', 'h'), 'ld (iy + d), h'),
            0x75: Op(lambda: self.ld_indexed_reg_from_reg('iy', 'l'), 'ld (iy + d), l'),
            0x77: Op(lambda: self.ld_indexed_reg_from_reg('iy', 'a'), 'ld (iy + d), a'),
            0x7e: Op(lambda: self.ld_reg_indexed_addr('a', 'iy'), 'ld a, (iy + d)'),

            0xe1: Op(lambda: self.pop_indexed('iy'), 'pop iy'),
            0xe3: Op(lambda: self.ex_sp_indirect_index_reg('iy'), 'ex (sp), iy'),
            0xe6: Op(lambda: self.push_indexed('iy'), 'push iy'),

            0xf9: Op(lambda: self.ld_sp_indexed_16reg('iy'), 'ld sp, iy')
        }

    def single_cycle(self):
        operation = self.get_operation()
        operation.function()

    def get_operation(self):
        op_code = self.get_value_at_pc()
        operation = self.operations_by_opcode[op_code]
        if isinstance(operation, dict):
            op_code = self.get_value_at_pc()
            operation = operation[op_code]
        return operation

    def get_address_at_pc(self):
        return [self.get_value_at_pc(), self.get_value_at_pc()]

    def get_value_at_pc(self):
        op_code = self.memory.peek(self.special_registers['pc'])
        self.increment('pc')
        return op_code

    def increment(self, register_name):
        self.special_registers[register_name] += 1

    def ld_reg_from_reg(self, destination, source):
        self.main_registers[destination] = self.main_registers[source]

    def ld_reg_from_reg_indirect(self, destination, source_register):
        address = self.get_indirect_address(source_register)
        self.main_registers[destination] = self.memory.peek(address)

    def ld_reg_indirect_from_reg(self, destination_register, source_register):
        address = self.get_indirect_address(destination_register)
        self.memory.poke(address, self.main_registers[source_register])

    def ld_a_i(self):
        self.main_registers['a'] = self.special_registers['i']

    def ld_reg_immediate(self, destination_register):
        operand = self.get_value_at_pc()
        self.main_registers[destination_register] = operand

    def ld_reg_indexed_addr(self, destination_register, index_register):
        operand = self.get_value_at_pc()
        offset = twos_complement(operand)
        self.main_registers[destination_register] = self.memory.peek(self.index_registers[index_register] + offset)

    def ld_indexed_reg_from_reg(self, destination_index_register, source_register):
        operand = self.get_value_at_pc()
        offset = twos_complement(operand)
        self.memory.poke(self.index_registers[destination_index_register] + offset, self.main_registers[source_register])

    def ld_hl_indirect_immediate(self):
        operand = self.get_value_at_pc()
        self.memory.poke(self.get_indirect_address('hl'), operand)

    def ld_a_ext_addr(self):
        little_endian_address = self.get_address_at_pc()
        self.main_registers['a'] = self.memory.peek(big_endian_value(little_endian_address))

    def ld_ext_addr_a(self):
        little_endian_address = self.get_address_at_pc()
        self.memory.poke(big_endian_value(little_endian_address), self.main_registers['a'])

    def ld_indexed_addr_immediate(self, index_register):
        operand = self.get_value_at_pc()
        immediate_value = self.get_value_at_pc()

        offset = twos_complement(operand)
        self.memory.poke(self.index_registers[index_register] + offset, immediate_value)

    def ld_16reg_immediate(self, register_pair):
        lsb = self.get_value_at_pc()
        msb = self.get_value_at_pc()
        self.main_registers[register_pair[0]] = msb
        self.main_registers[register_pair[1]] = lsb

    def ld_sp_immediate(self):
        little_endian_address = self.get_address_at_pc()
        self.special_registers['sp'] = big_endian_value(little_endian_address)

    def ld_sp_indexed_16reg(self, source_register_pair):
        self.special_registers['sp'] = self.index_registers[source_register_pair]

    def ld_sp_hl(self):
        self.special_registers['sp'] = big_endian_value([self.main_registers['l'], self.main_registers['h']])

    def ld_indexed_reg_immediate(self, index_register):
        little_endian_address = self.get_address_at_pc()
        self.index_registers[index_register] = big_endian_value(little_endian_address)

    def ld_ext_indexed_16reg(self, source_register_pair):
        dest_address = big_endian_value(self.get_address_at_pc())
        self.memory.poke(dest_address, self.index_registers[source_register_pair] & 0xff)
        self.memory.poke(dest_address + 1, self.index_registers[source_register_pair] >> 8)

    def ld_ext_sp(self):
        dest_address = big_endian_value(self.get_address_at_pc())
        self.memory.poke(dest_address, self.special_registers['sp'] & 0xff)
        self.memory.poke(dest_address + 1, self.special_registers['sp'] >> 8)

    def ld_ext_16reg(self, source_register_pair):
        dest_address = big_endian_value(self.get_address_at_pc())
        self.memory.poke(dest_address, self.main_registers[source_register_pair[1]])
        self.memory.poke(dest_address + 1, self.main_registers[source_register_pair[0]])

    def ld_indexed_16reg_ext(self, dest_register_pair):
        src_address = big_endian_value(self.get_address_at_pc())
        low_byte = self.memory.peek(src_address)
        high_byte = self.memory.peek(src_address + 1)
        self.index_registers[dest_register_pair] = big_endian_value([low_byte, high_byte])

    def ld_sp_ext(self):
        src_address = big_endian_value(self.get_address_at_pc())
        low_byte = self.memory.peek(src_address)
        high_byte = self.memory.peek(src_address + 1)
        self.special_registers['sp'] = big_endian_value([low_byte, high_byte])

    def ld_16reg_ext(self, dest_register_pair):
        src_address = big_endian_value(self.get_address_at_pc())
        low_byte = self.memory.peek(src_address)
        high_byte = self.memory.peek(src_address + 1)
        self.main_registers[dest_register_pair[0]] = high_byte
        self.main_registers[dest_register_pair[1]] = low_byte

    def push_indexed(self, register_pair):
        self.push_byte(self.index_registers[register_pair] >> 8)
        self.push_byte(self.index_registers[register_pair] & 0xff)

    def push(self, register_pair):
        self.push_byte(self.main_registers[register_pair[0]])
        self.push_byte(self.main_registers[register_pair[1]])

    def push_byte(self, byte):
        if self.special_registers['sp'] == 0:
            self.special_registers['sp'] = 0xffff
        else:
            self.special_registers['sp'] -= 1
        self.memory.poke(self.special_registers['sp'], byte)

    def pop_indexed(self, register_pair):
        lsb = self.pop_byte()
        msb = self.pop_byte()
        self.index_registers[register_pair] = big_endian_value([lsb, msb])

    def pop(self, register_pair):
        lsb = self.pop_byte()
        msb = self.pop_byte()
        self.main_registers[register_pair[0]] = msb
        self.main_registers[register_pair[1]] = lsb

    def pop_byte(self):
        byte = self.memory.peek(self.special_registers['sp'])
        if self.special_registers['sp'] == 0xffff:
            self.special_registers['sp'] = 0
        else:
            self.special_registers['sp'] += 1
        return byte

    def ex_de_hl(self):
        old_h = self.main_registers['h']
        old_l = self.main_registers['l']
        self.main_registers['h'] = self.main_registers['d']
        self.main_registers['l'] = self.main_registers['e']
        self.main_registers['d'] = old_h
        self.main_registers['e'] = old_l

    def ex_af_alt_af(self):
        self.ex_with_alternate('af')

    def exx(self):
        self.ex_with_alternate('bc')
        self.ex_with_alternate('de')
        self.ex_with_alternate('hl')

    def ex_sp_indirect_hl(self):
        old_h = self.main_registers['h']
        old_l = self.main_registers['l']

        self.main_registers['h'] = self.memory.peek(self.special_registers['sp'] + 1)
        self.main_registers['l'] = self.memory.peek(self.special_registers['sp'])

        self.memory.poke(self.special_registers['sp'], old_l)
        self.memory.poke(self.special_registers['sp'] + 1, old_h)

    def ex_with_alternate(self, register_pair):
        old_main = [self.main_registers[register_pair[0]], self.main_registers[register_pair[1]]]
        self.main_registers[register_pair[0]] = self.alternate_registers[register_pair[0]]
        self.main_registers[register_pair[1]] = self.alternate_registers[register_pair[1]]
        self.alternate_registers[register_pair[0]] = old_main[0]
        self.alternate_registers[register_pair[1]] = old_main[1]

    def ex_sp_indirect_index_reg(self, register):
        old_index = self.index_registers[register]
        self.index_registers[register] = big_endian_value([self.memory.peek(self.special_registers['sp']),
                                                           self.memory.peek(self.special_registers['sp'] + 1)])
        self.memory.poke(self.special_registers['sp'], old_index & 0xff)
        self.memory.poke(self.special_registers['sp'] + 1, old_index >> 8)

    def ldi(self):
        src_addr = self.get_indirect_address('hl')
        tgt_addr = self.get_indirect_address('de')

        self.memory.poke(tgt_addr, self.memory.peek(src_addr))

        src_addr = (src_addr + 1) % 0x10000
        tgt_addr = (tgt_addr + 1) % 0x10000

        self.main_registers['h'] = src_addr >> 8
        self.main_registers['l'] = src_addr & 0xff
        self.main_registers['d'] = tgt_addr >> 8
        self.main_registers['e'] = tgt_addr & 0xff

        counter = self.get_indirect_address('bc')
        counter = (counter - 1) % 0x10000

        self.main_registers['b'] = counter >> 8
        self.main_registers['c'] = counter & 0xff

        self.set_condition('h', False)
        self.set_condition('p', counter != 0)
        self.set_condition('n', False)

    def set_condition(self, flag, value):
        mask = self.condition_masks[flag]
        if value:
            self.main_registers['f'] = self.main_registers['f'] | mask
        else:
            self.main_registers['f'] = self.main_registers['f'] & (0xff ^ mask)

    def condition(self, flag):
        mask = self.condition_masks[flag]
        return self.main_registers['f'] & mask > 0

    def get_indirect_address(self, register_pair):
        msb = self.main_registers[register_pair[0]]
        lsb = self.main_registers[register_pair[1]]
        return big_endian_value([lsb, msb])