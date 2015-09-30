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

            0x4f: Op(lambda: self.register_load('c', 'a'), 'ld c, a'),
            0x48: Op(lambda: self.register_load('c', 'b'), 'ld c, b'),
            0x49: Op(lambda: self.register_load('c', 'c'), 'ld c, c'),
            0x4a: Op(lambda: self.register_load('c', 'd'), 'ld c, d'),
            0x4b: Op(lambda: self.register_load('c', 'e'), 'ld c, e'),
            0x4c: Op(lambda: self.register_load('c', 'f'), 'ld c, f'),
            0x4d: Op(lambda: self.register_load('c', 'l'), 'ld c, l'),

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