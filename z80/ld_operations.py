from baseop import BaseOp
from z80.funcs import big_endian_value, high_low_pair, to_signed


class OpLd16RegImmediate(BaseOp):
    def __init__(self, processor, memory, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.reg = reg

    def execute(self):
        lsb = self.processor.get_next_byte()
        msb = self.processor.get_next_byte()
        self.processor.main_registers[self.reg[0]] = msb
        self.processor.main_registers[self.reg[1]] = lsb

    def t_states(self):
        return 10

    def __str__(self):
        return 'ld {}, nn'.format(self.reg)


class OpLd16RegIndirectFrom8Reg(BaseOp):
    def __init__(self, processor, memory, destination_reg, source_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.destination_reg = destination_reg
        self.source_reg = source_reg

    def execute(self):
        address = self.processor.get_16bit_reg(self.destination_reg)
        self.memory[0xffff & address] = self.processor.main_registers[self.source_reg]

    def t_states(self):
        return 7

    def __str__(self):
        return 'ld ({}), {}'.format(self.destination_reg, self.source_reg)


class OpLd8RegImmediate(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self):
        operand = self.processor.get_next_byte()
        self.processor.main_registers[self.reg] = operand

    def t_states(self):
        return 7

    def __str__(self):
        return 'ld {}, n'.format(self.reg)


class OpLd8RegFrom16RegIndirect(BaseOp):
    def __init__(self, processor, memory, destination_reg, source_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.destination_reg = destination_reg
        self.source_reg = source_reg

    def execute(self):
        address = self.processor.get_16bit_reg(self.source_reg)
        self.processor.main_registers[self.destination_reg] = self.memory[0xffff & address]

    def t_states(self):
        return 7

    def __str__(self):
        return 'ld {}, ({})'.format(self.source_reg, self.destination_reg)


class OpLd8RegFrom8Reg(BaseOp):
    def __init__(self, processor, destination_reg, source_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.destination_reg = destination_reg
        self.source_reg = source_reg

    def execute(self):
        self.processor.main_registers[self.destination_reg] = self.processor.main_registers[self.source_reg]

    def t_states(self):
        return 4

    def __str__(self):
        return 'ld {}, {}'.format(self.destination_reg, self.source_reg)


class OpLdAddressA(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        little_endian_address = self.processor.get_address_at_pc()
        self.memory[0xffff & big_endian_value(little_endian_address)] = self.processor.main_registers['a']

    def t_states(self):
        return 13

    def __str__(self):
        return 'ld (nn), a'


class OpLdAAddress(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        little_endian_address = self.processor.get_address_at_pc()
        self.processor.main_registers['a'] = self.memory[0xffff & big_endian_value(little_endian_address)]

    def t_states(self):
        return 13

    def __str__(self):
        return 'ld a, (nn)'


class OpLdAddress16Reg(BaseOp):
    def __init__(self, processor, memory, source_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.source_reg = source_reg

    def execute(self):
        dest_address = big_endian_value(self.processor.get_address_at_pc())
        self.memory[0xffff & dest_address] = self.processor.main_registers[self.source_reg[1]]
        self.memory[0xffff & dest_address + 1] = self.processor.main_registers[self.source_reg[0]]

    def t_states(self):
        return 20

    def __str__(self):
        return 'ld (nn), {}'.format(self.source_reg)


class OpLdAddressHl(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        dest_address = big_endian_value(self.processor.get_address_at_pc())
        self.memory[0xffff & dest_address] = self.processor.main_registers['l']
        self.memory[0xffff & dest_address + 1] = self.processor.main_registers['h']

    def t_states(self):
        return 16

    def __str__(self):
        return 'ld (nn), hl'


class OpLd16RegAddress(BaseOp):
    def __init__(self, processor, memory, destination_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.destination_reg = destination_reg

    def execute(self):
        src_address = big_endian_value(self.processor.get_address_at_pc())
        low_byte = self.memory[0xffff & src_address]
        high_byte = self.memory[0xffff & (src_address + 1)]
        self.processor.main_registers[self.destination_reg[0]] = high_byte
        self.processor.main_registers[self.destination_reg[1]] = low_byte

    def t_states(self):
        return 20

    def __str__(self):
        return 'ld {}, (nn)'.format(self.destination_reg)


class OpLdHlAddress(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        src_address = big_endian_value(self.processor.get_address_at_pc())
        low_byte = self.memory[0xffff & src_address]
        high_byte = self.memory[0xffff & (src_address + 1)]
        self.processor.main_registers['h'] = high_byte
        self.processor.main_registers['l'] = low_byte

    def t_states(self):
        return 16

    def __str__(self):
        return 'ld hl, (nn)'


class OpLdSpImmediate(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        little_endian_address = self.processor.get_address_at_pc()
        self.processor.special_registers['sp'] = big_endian_value(little_endian_address)

    def t_states(self):
        pass

    def __str__(self):
        return 'ld sp, nn'


class OpLdSpHl(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        self.processor.special_registers['sp'] = big_endian_value([self.processor.main_registers['l'],
                                                                   self.processor.main_registers['h']])

    def t_states(self):
        return 6

    def __str__(self):
        return 'ld sp, hl'


class OpLdHlIndirectImmediate(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        operand = self.processor.get_next_byte()
        self.memory[0xffff & self.processor.get_16bit_reg('hl')] = operand

    def t_states(self):
        return 10

    def __str__(self):
        return 'ld (hl), n'


class OpLdExtSp(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        dest_address = big_endian_value(self.processor.get_address_at_pc())
        high_byte, low_byte = high_low_pair(self.processor.special_registers['sp'])
        self.memory[0xffff & dest_address] = low_byte
        self.memory[0xffff & (dest_address + 1)] = high_byte

    def t_states(self):
        return 20

    def __str__(self):
        return 'ld (nn), sp'


class OpLdSpExt(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        src_address = big_endian_value(self.processor.get_address_at_pc())
        low_byte = self.memory[0xffff & src_address]
        high_byte = self.memory[0xffff & (src_address + 1)]
        self.processor.special_registers['sp'] = big_endian_value([low_byte, high_byte])

    def t_states(self):
        return 20

    def __str__(self):
        return 'ld sp, (nn)'


class OpLdIndexedImmediate(BaseOp):
    def __init__(self, processor, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.indexed_reg = indexed_reg

    def execute(self):
        little_endian_address = self.processor.get_address_at_pc()
        self.processor.index_registers[self.indexed_reg] = big_endian_value(little_endian_address)

    def t_states(self):
        return 14

    def __str__(self):
        return 'ld {}, nn'.format(self.indexed_reg)


class OpLdExtIndexed(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self):
        dest_address = big_endian_value(self.processor.get_address_at_pc())
        high_byte, low_byte = high_low_pair(self.processor.index_registers[self.indexed_reg])
        self.memory[0xffff & dest_address] = low_byte
        self.memory[0xffff & (dest_address + 1)] = high_byte

    def t_states(self):
        return 20

    def __str__(self):
        return 'ld (nn), {}'.format(self.indexed_reg)


class OpLdIndexedExt(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self):
        src_address = big_endian_value(self.processor.get_address_at_pc())
        low_byte = self.memory[0xffff & src_address]
        high_byte = self.memory[0xffff & (src_address + 1)]
        self.processor.index_registers[self.indexed_reg] = big_endian_value([low_byte, high_byte])

    def t_states(self):
        return 20

    def __str__(self):
        return 'ld {}, (nn)'.format(self.indexed_reg)


class OpLdIndexedIndirectImmediate(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self):
        operand = self.processor.get_next_byte()
        immediate_value = self.processor.get_next_byte()

        offset = to_signed(operand)
        self.memory[0xffff & (self.processor.index_registers[self.indexed_reg] + offset)] = immediate_value

    def t_states(self):
        return 19

    def __str__(self):
        return 'ld ({} + d), n'


class OpLd8RegIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, destination_reg, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.destination_reg = destination_reg
        self.indexed_reg = indexed_reg

    def execute(self):
        operand = self.processor.get_next_byte()
        offset = to_signed(operand)
        self.processor.main_registers[self.destination_reg] = self.memory[
            0xffff & (self.processor.index_registers[self.indexed_reg] + offset)]

    def t_states(self):
        return 19

    def __str__(self):
        return 'ld {}, ({} + d)'.format(self.destination_reg, self.indexed_reg)


class OpLdIndexedIndirect8Reg(BaseOp):
    def __init__(self, processor, memory, indexed_reg, source_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg
        self.source_reg = source_reg

    def execute(self):
        operand = self.processor.get_next_byte()
        offset = to_signed(operand)
        self.memory[0xffff & (self.processor.index_registers[self.indexed_reg] + offset)] = \
            self.processor.main_registers[self.source_reg]

    def t_states(self):
        return 19

    def __str__(self):
        return 'ld ({} + d), {}'.format(self.indexed_reg, self.source_reg)


class OpLdSpIndexed(BaseOp):
    def __init__(self, processor, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.indexed_reg = indexed_reg

    def execute(self):
        self.processor.special_registers['sp'] = self.processor.index_registers[self.indexed_reg]

    def t_states(self):
        return 10

    def __str__(self):
        return 'ld sp, {}'.format(self.indexed_reg)
