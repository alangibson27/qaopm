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

    def build_swappable_register_set(self):
        return {'a': 0x0, 'f': 0x0, 'b': 0x0, 'c': 0x0, 'd': 0x0, 'e': 0x0, 'h': 0x0, 'l': 0x0}

    def build_index_register_set(self):
        return {'ix': 0x0000, 'iy': 0x0000}

    def build_special_register_set(self):
        return {'i': 0x0, 'r': 0x0, 'ix': 0x0000, 'iy': 0x0000, 'sp': 0xffff, 'pc': 0x0000}

    def create_ld_reg_from_reg(self, destination, source):
        return Op(lambda: self.ld_reg_from_reg(destination, source), 'ld {}, {}'.format(destination, source))

    def create_ld_reg_from_reg_indirect(self, destination, source_register):
        return Op(lambda: self.ld_reg_from_reg_indirect(destination, source_register), 'ld {}, ({})'.format(destination, source_register))

    def create_ld_reg_indirect_from_reg(self, destination_register, source_register):
        return Op(lambda: self.ld_reg_indirect_from_reg(destination_register, source_register), 'ld ({}), {}'.format(destination_register, source_register))

    def init_opcode_map(self):
        return {
            0x02: self.create_ld_reg_indirect_from_reg('bc', 'a'),
            0x06: Op(lambda: self.ld_reg_immediate('b'), 'ld b, n'),
            0x0a: self.create_ld_reg_from_reg_indirect('a', 'bc'),
            0x0e: Op(lambda: self.ld_reg_immediate('c'), 'ld c, n'),

            0x12: self.create_ld_reg_indirect_from_reg('de', 'a'),
            0x16: Op(lambda: self.ld_reg_immediate('d'), 'ld d, n'),
            0x1a: self.create_ld_reg_from_reg_indirect('a', 'de'),
            0x1e: Op(lambda: self.ld_reg_immediate('e'), 'ld e, n'),

            0x26: Op(lambda: self.ld_reg_immediate('h'), 'ld h, n'),
            0x2e: Op(lambda: self.ld_reg_immediate('l'), 'ld l, n'),

            0x36: Op(lambda: self.ld_hl_indirect_immediate(), 'ld (hl), n'),
            0x3a: Op(lambda: self.ld_a_ext_addr(), 'ld a, (nn)'),
            0x3e: Op(lambda: self.ld_reg_immediate('a'), 'ld a, n'),

            0x40: self.create_ld_reg_from_reg('b', 'b'),
            0x41: self.create_ld_reg_from_reg('b', 'c'),
            0x42: self.create_ld_reg_from_reg('b', 'd'),
            0x43: self.create_ld_reg_from_reg('b', 'e'),
            0x44: self.create_ld_reg_from_reg('b', 'f'),
            0x45: self.create_ld_reg_from_reg('b', 'l'),
            0x46: self.create_ld_reg_from_reg_indirect('b', 'hl'),
            0x47: self.create_ld_reg_from_reg('b', 'a'),

            0x48: self.create_ld_reg_from_reg('c', 'b'),
            0x49: self.create_ld_reg_from_reg('c', 'c'),
            0x4a: self.create_ld_reg_from_reg('c', 'd'),
            0x4b: self.create_ld_reg_from_reg('c', 'e'),
            0x4c: self.create_ld_reg_from_reg('c', 'f'),
            0x4d: self.create_ld_reg_from_reg('c', 'l'),
            0x4e: self.create_ld_reg_from_reg_indirect('c', 'hl'),
            0x4f: self.create_ld_reg_from_reg('c', 'a'),

            0x50: self.create_ld_reg_from_reg('d', 'b'),
            0x51: self.create_ld_reg_from_reg('d', 'c'),
            0x52: self.create_ld_reg_from_reg('d', 'd'),
            0x53: self.create_ld_reg_from_reg('d', 'e'),
            0x54: self.create_ld_reg_from_reg('d', 'f'),
            0x55: self.create_ld_reg_from_reg('d', 'l'),
            0x56: self.create_ld_reg_from_reg_indirect('d', 'hl'),
            0x57: self.create_ld_reg_from_reg('d', 'a'),

            0x58: self.create_ld_reg_from_reg('e', 'b'),
            0x59: self.create_ld_reg_from_reg('e', 'c'),
            0x5a: self.create_ld_reg_from_reg('e', 'd'),
            0x5b: self.create_ld_reg_from_reg('e', 'e'),
            0x5c: self.create_ld_reg_from_reg('e', 'f'),
            0x5d: self.create_ld_reg_from_reg('e', 'l'),
            0x5e: self.create_ld_reg_from_reg_indirect('e', 'hl'),
            0x5f: self.create_ld_reg_from_reg('e', 'a'),

            0x60: self.create_ld_reg_from_reg('h', 'b'),
            0x61: self.create_ld_reg_from_reg('h', 'c'),
            0x62: self.create_ld_reg_from_reg('h', 'd'),
            0x63: self.create_ld_reg_from_reg('h', 'e'),
            0x64: self.create_ld_reg_from_reg('h', 'f'),
            0x65: self.create_ld_reg_from_reg('h', 'l'),
            0x66: self.create_ld_reg_from_reg_indirect('h', 'hl'),
            0x67: self.create_ld_reg_from_reg('h', 'a'),

            0x68: self.create_ld_reg_from_reg('l', 'b'),
            0x69: self.create_ld_reg_from_reg('l', 'c'),
            0x6a: self.create_ld_reg_from_reg('l', 'd'),
            0x6b: self.create_ld_reg_from_reg('l', 'e'),
            0x6c: self.create_ld_reg_from_reg('l', 'f'),
            0x6d: self.create_ld_reg_from_reg('l', 'l'),
            0x6e: self.create_ld_reg_from_reg_indirect('l', 'hl'),
            0x6f: self.create_ld_reg_from_reg('l', 'a'),

            0x70: self.create_ld_reg_indirect_from_reg('hl', 'b'),
            0x71: self.create_ld_reg_indirect_from_reg('hl', 'c'),
            0x72: self.create_ld_reg_indirect_from_reg('hl', 'd'),
            0x73: self.create_ld_reg_indirect_from_reg('hl', 'e'),
            0x74: self.create_ld_reg_indirect_from_reg('hl', 'f'),
            0x75: self.create_ld_reg_indirect_from_reg('hl', 'l'),
            0x77: self.create_ld_reg_indirect_from_reg('hl', 'a'),

            0x78: self.create_ld_reg_from_reg('a', 'b'),
            0x79: self.create_ld_reg_from_reg('a', 'c'),
            0x7a: self.create_ld_reg_from_reg('a', 'd'),
            0x7b: self.create_ld_reg_from_reg('a', 'e'),
            0x7c: self.create_ld_reg_from_reg('a', 'f'),
            0x7d: self.create_ld_reg_from_reg('a', 'l'),
            0x7e: self.create_ld_reg_from_reg_indirect('a', 'hl'),
            0x7f: self.create_ld_reg_from_reg('a', 'a'),

            0xed: self.init_ed_opcodes(),
            0xdd: self.init_dd_opcodes(),
            0xfd: self.init_fd_opcodes()
        }

    def init_ed_opcodes(self):
        return {
            0x57: Op(self.ld_a_i, 'ld a, i')
        }

    def init_dd_opcodes(self):
        return {
            0x46: Op(lambda: self.ld_reg_indexed('b', 'ix'), 'ld b, (ix + d)'),
            0x4e: Op(lambda: self.ld_reg_indexed('c', 'ix'), 'ld c, (ix + d)'),
            0x56: Op(lambda: self.ld_reg_indexed('d', 'ix'), 'ld d, (ix + d)'),
            0x5e: Op(lambda: self.ld_reg_indexed('e', 'ix'), 'ld e, (ix + d)'),
            0x66: Op(lambda: self.ld_reg_indexed('h', 'ix'), 'ld h, (ix + d)'),
            0x6e: Op(lambda: self.ld_reg_indexed('l', 'ix'), 'ld l, (ix + d)'),
            0x7e: Op(lambda: self.ld_reg_indexed('a', 'ix'), 'ld a, (ix + d)')
        }

    def init_fd_opcodes(self):
        return {
            0x46: Op(lambda: self.ld_reg_indexed('b', 'iy'), 'ld b, (iy + d)'),
            0x4e: Op(lambda: self.ld_reg_indexed('c', 'iy'), 'ld c, (iy + d)'),
            0x56: Op(lambda: self.ld_reg_indexed('d', 'iy'), 'ld d, (iy + d)'),
            0x5e: Op(lambda: self.ld_reg_indexed('e', 'iy'), 'ld e, (iy + d)'),
            0x66: Op(lambda: self.ld_reg_indexed('h', 'iy'), 'ld h, (iy + d)'),
            0x6e: Op(lambda: self.ld_reg_indexed('l', 'iy'), 'ld l, (iy + d)'),
            0x7e: Op(lambda: self.ld_reg_indexed('a', 'iy'), 'ld a, (iy + d)')
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

    def ld_reg_indexed(self, destination_register, index_register):
        operand = self.get_value_at_pc()
        offset = twos_complement(operand)

        self.main_registers[destination_register] = self.memory.peek(self.index_registers[index_register] + offset)

    def ld_hl_indirect_immediate(self):
        operand = self.get_value_at_pc()
        self.memory.poke(self.get_indirect_address('hl'), operand)

    def ld_a_ext_addr(self):
        msb = self.get_value_at_pc()
        lsb = self.get_value_at_pc()
        self.main_registers['a'] = self.memory.peek(big_endian_value(msb, lsb))

    def get_indirect_address(self, register_pair):
        msb = self.main_registers[register_pair[0]]
        lsb = self.main_registers[register_pair[1]]
        return big_endian_value(msb, lsb)

