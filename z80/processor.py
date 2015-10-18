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

    def create_register_load(self, destination, source):
        return Op(lambda: self.register_load(destination, source), 'ld {}, {}'.format(destination, source))

    def create_register_load_memory(self, destination, source_register):
        return Op(lambda: self.register_load_memory(destination, source_register), 'ld {}, ({})'.format(destination, source_register))

    def create_memory_load_indirect(self, destination_register, source_register):
        return Op(lambda: self.memory_load_indirect(destination_register, source_register), 'ld ({}), {}'.format(destination_register, source_register))

    def init_opcode_map(self):
        return {
            0x7f: self.create_register_load('a', 'a'),
            0x78: self.create_register_load('a', 'b'),
            0x79: self.create_register_load('a', 'c'),
            0x7a: self.create_register_load('a', 'd'),
            0x7b: self.create_register_load('a', 'e'),
            0x7c: self.create_register_load('a', 'f'),
            0x7d: self.create_register_load('a', 'l'),
            0x7e: self.create_register_load_memory('a', 'hl'),
            0x0a: self.create_register_load_memory('a', 'bc'),
            0x1a: self.create_register_load_memory('a', 'de'),

            0x47: self.create_register_load('b', 'a'),
            0x40: self.create_register_load('b', 'b'),
            0x41: self.create_register_load('b', 'c'),
            0x42: self.create_register_load('b', 'd'),
            0x43: self.create_register_load('b', 'e'),
            0x44: self.create_register_load('b', 'f'),
            0x45: self.create_register_load('b', 'l'),
            0x46: self.create_register_load_memory('b', 'hl'),

            0x4f: self.create_register_load('c', 'a'),
            0x48: self.create_register_load('c', 'b'),
            0x49: self.create_register_load('c', 'c'),
            0x4a: self.create_register_load('c', 'd'),
            0x4b: self.create_register_load('c', 'e'),
            0x4c: self.create_register_load('c', 'f'),
            0x4d: self.create_register_load('c', 'l'),
            0x4e: self.create_register_load_memory('c', 'hl'),

            0x57: self.create_register_load('d', 'a'),
            0x50: self.create_register_load('d', 'b'),
            0x51: self.create_register_load('d', 'c'),
            0x52: self.create_register_load('d', 'd'),
            0x53: self.create_register_load('d', 'e'),
            0x54: self.create_register_load('d', 'f'),
            0x55: self.create_register_load('d', 'l'),
            0x56: self.create_register_load_memory('d', 'hl'),

            0x5f: self.create_register_load('e', 'a'),
            0x58: self.create_register_load('e', 'b'),
            0x59: self.create_register_load('e', 'c'),
            0x5a: self.create_register_load('e', 'd'),
            0x5b: self.create_register_load('e', 'e'),
            0x5c: self.create_register_load('e', 'f'),
            0x5d: self.create_register_load('e', 'l'),
            0x5e: self.create_register_load_memory('e', 'hl'),

            0x67: self.create_register_load('h', 'a'),
            0x60: self.create_register_load('h', 'b'),
            0x61: self.create_register_load('h', 'c'),
            0x62: self.create_register_load('h', 'd'),
            0x63: self.create_register_load('h', 'e'),
            0x64: self.create_register_load('h', 'f'),
            0x65: self.create_register_load('h', 'l'),
            0x66: self.create_register_load_memory('h', 'hl'),

            0x6f: self.create_register_load('l', 'a'),
            0x68: self.create_register_load('l', 'b'),
            0x69: self.create_register_load('l', 'c'),
            0x6a: self.create_register_load('l', 'd'),
            0x6b: self.create_register_load('l', 'e'),
            0x6c: self.create_register_load('l', 'f'),
            0x6d: self.create_register_load('l', 'l'),
            0x6e: self.create_register_load_memory('l', 'hl'),

            0x77: self.create_memory_load_indirect('hl', 'a'),
            0x70: self.create_memory_load_indirect('hl', 'b'),
            0x71: self.create_memory_load_indirect('hl', 'c'),
            0x72: self.create_memory_load_indirect('hl', 'd'),
            0x73: self.create_memory_load_indirect('hl', 'e'),
            0x74: self.create_memory_load_indirect('hl', 'f'),
            0x75: self.create_memory_load_indirect('hl', 'l'),

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
        address = self.get_indirect_address(source_register)
        self.main_registers[destination] = self.memory.peek(address)

    def memory_load_indirect(self, destination_register, source_register):
        address = self.get_indirect_address(destination_register)
        self.memory.poke(address, self.main_registers[source_register])

    def ld_a_i(self):
        self.main_registers['a'] = self.special_registers['i']

    def get_indirect_address(self, register_pair):
        msb = self.main_registers[register_pair[0]]
        lsb = self.main_registers[register_pair[1]]
        return (msb << 8) + lsb
