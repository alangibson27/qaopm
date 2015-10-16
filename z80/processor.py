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
        self.operations_by_opcode = self.init_opcode_map()

    def build_swappable_register_set(self):
        return {'a': 0x0, 'f': 0x0, 'b': 0x0, 'c': 0x0, 'd': 0x0, 'e': 0x0, 'h': 0x0, 'l': 0x0}

    def build_special_register_set(self):
        return {'i': 0x0, 'r': 0x0, 'ix': 0x0000, 'iy': 0x0000, 'sp': 0xffff, 'pc': 0x0000}

    def init_opcode_map(self):
        return {
            0x7f: Op(lambda: self.register_load('a', 'a'), 'ld a, a'),
            0x78: Op(lambda: self.register_load('a', 'b'), 'ld a, b'),
            0x79: Op(lambda: self.register_load('a', 'c'), 'ld a, c'),
            0x7a: Op(lambda: self.register_load('a', 'd'), 'ld a, d'),
            0x7b: Op(lambda: self.register_load('a', 'e'), 'ld a, e'),
            0x7c: Op(lambda: self.register_load('a', 'f'), 'ld a, f'),
            0x7d: Op(lambda: self.register_load('a', 'l'), 'ld a, l'),
            0x7e: Op(lambda: self.register_load_memory('a', 'hl'), 'ld a, (hl)'),
            0x0a: Op(lambda: self.register_load_memory('a', 'bc'), 'ld a, (bc)'),
            0x1a: Op(lambda: self.register_load_memory('a', 'de'), 'ld a, (de)'),

            0x47: Op(lambda: self.register_load('b', 'a'), 'ld b, a'),
            0x40: Op(lambda: self.register_load('b', 'b'), 'ld b, b'),
            0x41: Op(lambda: self.register_load('b', 'c'), 'ld b, c'),
            0x42: Op(lambda: self.register_load('b', 'd'), 'ld b, d'),
            0x43: Op(lambda: self.register_load('b', 'e'), 'ld b, e'),
            0x44: Op(lambda: self.register_load('b', 'f'), 'ld b, f'),
            0x45: Op(lambda: self.register_load('b', 'l'), 'ld b, l'),
            0x46: Op(lambda: self.register_load_memory('b', 'hl'), 'ld b, (hl)'),

            0x4f: Op(lambda: self.register_load('c', 'a'), 'ld c, a'),
            0x48: Op(lambda: self.register_load('c', 'b'), 'ld c, b'),
            0x49: Op(lambda: self.register_load('c', 'c'), 'ld c, c'),
            0x4a: Op(lambda: self.register_load('c', 'd'), 'ld c, d'),
            0x4b: Op(lambda: self.register_load('c', 'e'), 'ld c, e'),
            0x4c: Op(lambda: self.register_load('c', 'f'), 'ld c, f'),
            0x4d: Op(lambda: self.register_load('c', 'l'), 'ld c, l'),
            0x4e: Op(lambda: self.register_load_memory('c', 'hl'), 'ld c, (hl)'),

            0x57: Op(lambda: self.register_load('d', 'a'), 'ld d, a'),
            0x50: Op(lambda: self.register_load('d', 'b'), 'ld d, b'),
            0x51: Op(lambda: self.register_load('d', 'c'), 'ld d, c'),
            0x52: Op(lambda: self.register_load('d', 'd'), 'ld d, d'),
            0x53: Op(lambda: self.register_load('d', 'e'), 'ld d, e'),
            0x54: Op(lambda: self.register_load('d', 'f'), 'ld d, f'),
            0x55: Op(lambda: self.register_load('d', 'l'), 'ld d, l'),
            0x56: Op(lambda: self.register_load_memory('d', 'hl'), 'ld d, (hl)'),

            0x5f: Op(lambda: self.register_load('e', 'a'), 'ld e, a'),
            0x58: Op(lambda: self.register_load('e', 'b'), 'ld e, b'),
            0x59: Op(lambda: self.register_load('e', 'c'), 'ld e, c'),
            0x5a: Op(lambda: self.register_load('e', 'd'), 'ld e, d'),
            0x5b: Op(lambda: self.register_load('e', 'e'), 'ld e, e'),
            0x5c: Op(lambda: self.register_load('e', 'f'), 'ld e, f'),
            0x5d: Op(lambda: self.register_load('e', 'l'), 'ld e, l'),
            0x5e: Op(lambda: self.register_load_memory('e', 'hl'), 'ld e, (hl)'),

            0x67: Op(lambda: self.register_load('h', 'a'), 'ld h, a'),
            0x60: Op(lambda: self.register_load('h', 'b'), 'ld h, b'),
            0x61: Op(lambda: self.register_load('h', 'c'), 'ld h, c'),
            0x62: Op(lambda: self.register_load('h', 'd'), 'ld h, d'),
            0x63: Op(lambda: self.register_load('h', 'e'), 'ld h, e'),
            0x64: Op(lambda: self.register_load('h', 'f'), 'ld h, f'),
            0x65: Op(lambda: self.register_load('h', 'l'), 'ld h, l'),
            0x66: Op(lambda: self.register_load_memory('h', 'hl'), 'ld h, (hl)'),

            0x6f: Op(lambda: self.register_load('l', 'a'), 'ld l, a'),
            0x68: Op(lambda: self.register_load('l', 'b'), 'ld l, b'),
            0x69: Op(lambda: self.register_load('l', 'c'), 'ld l, c'),
            0x6a: Op(lambda: self.register_load('l', 'd'), 'ld l, d'),
            0x6b: Op(lambda: self.register_load('l', 'e'), 'ld l, e'),
            0x6c: Op(lambda: self.register_load('l', 'f'), 'ld l, f'),
            0x6d: Op(lambda: self.register_load('l', 'l'), 'ld l, l'),
            0x6e: Op(lambda: self.register_load_memory('l', 'hl'), 'ld l, (hl)'),

            0xed: self.init_ed_opcodes()
        }

    def init_ed_opcodes(self):
        return {
            0x57: Op(self.ld_a_i, 'ld a, i')
        }

    def single_cycle(self):
        operation = self.get_operation()
        operation.function()

    def get_operation(self):
        op_code = self.get_op_code()
        operation = self.operations_by_opcode[op_code]
        if isinstance(operation, dict):
            op_code = self.get_op_code()
            operation = operation[op_code]

        return operation

    def get_op_code(self):
        op_code = self.memory.peek(self.special_registers['pc'])
        self.increment('pc')
        return op_code

    def increment(self, register_name):
        self.special_registers[register_name] += 1

    def register_load(self, destination, source):
        self.main_registers[destination] = self.main_registers[source]

    def register_load_memory(self, destination, source_register):
        msb = self.main_registers[source_register[0]]
        lsb = self.main_registers[source_register[1]]
        address = self.join(msb, lsb)
        self.main_registers[destination] = self.memory.peek(address)

    def ld_a_i(self):
        self.main_registers['a'] = self.special_registers['i']

    def join(self, msb, lsb):
        return (msb << 8) + lsb