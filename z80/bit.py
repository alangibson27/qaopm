from baseop import BaseOp


class OpBitReg(BaseOp):
    def __init__(self, processor, reg, bit_pos):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg
        self.bit_pos = bit_pos

    def execute(self):
        _bit(self.processor, self.processor.main_registers[self.reg], self.bit_pos)

    def t_states(self):
        return 8

    def __str__(self):
        return 'bit {}, {}'.format(self.bit_pos, self.reg)


class OpBitHlIndirect(BaseOp):
    def __init__(self, processor, memory, bit_pos):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.bit_pos = bit_pos

    def execute(self):
        _bit(self.processor, self.memory[0xffff & self.processor.get_16bit_reg('hl')], self.bit_pos)

    def t_states(self):
        return 12

    def __str__(self):
        return 'bit {}, (hl)'.format(self.bit_pos)


class OpBitIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg, bit_pos):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg
        self.bit_pos = bit_pos

    def execute(self):
        offset = self.processor.get_signed_offset_byte()
        address = self.processor.index_registers[self.indexed_reg] + offset
        _bit(self.processor, self.memory[0xffff & address], self.bit_pos)

    def t_states(self):
        return 20

    def __str__(self):
        return 'bit {}, ({} + d)'.format(self.bit_pos, self.indexed_reg)


def _bit(processor, value, bit_pos):
    processor.set_condition('z', value & (1 << bit_pos) == 0)
    processor.set_condition('h', True)
    processor.set_condition('n', False)


class OpResReg(BaseOp):
    def __init__(self, processor, reg, bit_pos):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg
        self.bit_pos = bit_pos

    def execute(self):
        self.processor.main_registers[self.reg] = _res(self.processor.main_registers[self.reg], self.bit_pos)

    def t_states(self):
        return 8

    def __str__(self):
        return 'res {}, {}'.format(self.bit_pos, self.reg)


class OpResHlIndirect(BaseOp):
    def __init__(self, processor, memory, bit_pos):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.bit_pos = bit_pos

    def execute(self):
        address = self.processor.get_16bit_reg('hl')
        self.memory[0xffff & address] = _res(self.memory[0xffff & address], self.bit_pos)

    def t_states(self):
        return 15

    def __str__(self):
        return 'res {}, (hl)'.format(self.bit_pos)


class OpResIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg, bit_pos):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg
        self.bit_pos = bit_pos

    def execute(self):
        offset = self.processor.get_signed_offset_byte()
        address = self.processor.index_registers[self.indexed_reg] + offset
        self.memory[0xffff & address] = _res(self.memory[0xffff & address], self.bit_pos)

    def t_states(self):
        return 23

    def __str__(self):
        return 'res {}, ({} + d)'.format(self.bit_pos, self.indexed_reg)


def _res(value, bit_pos):
    return value & (0xff - (1 << bit_pos))


class OpSetReg(BaseOp):
    def __init__(self, processor, reg, bit_pos):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg
        self.bit_pos = bit_pos

    def execute(self):
        self.processor.main_registers[self.reg] = _set(self.processor.main_registers[self.reg], self.bit_pos)

    def t_states(self):
        return 8

    def __str__(self):
        return 'set {}, {}'.format(self.bit_pos, self.reg)


class OpSetHlIndirect(BaseOp):
    def __init__(self, processor, memory, bit_pos):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.bit_pos = bit_pos

    def execute(self):
        address = self.processor.get_16bit_reg('hl')
        self.memory[0xffff & address] = _set(self.memory[0xffff & address], self.bit_pos)

    def t_states(self):
        return 15

    def __str__(self):
        return 'set {}, (hl)'.format(self.bit_pos)


class OpSetIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg, bit_pos):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg
        self.bit_pos = bit_pos

    def execute(self):
        offset = self.processor.get_signed_offset_byte()
        address = self.processor.index_registers[self.indexed_reg] + offset
        self.memory[0xffff & address] = _set(self.memory[0xffff & address], self.bit_pos)

    def t_states(self):
        return 23

    def __str__(self):
        return 'set {}, ({} + d)'.format(self.bit_pos, self.indexed_reg)


def _set(value, bit_pos):
    return value | (1 << bit_pos)