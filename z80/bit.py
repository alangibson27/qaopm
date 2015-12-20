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
        pass

    def __str__(self):
        return 'bit {}, {}'.format(self.bit_pos, self.reg)


class OpBitHlIndirect(BaseOp):
    def __init__(self, processor, memory, bit_pos):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.bit_pos = bit_pos

    def execute(self):
        _bit(self.processor, self.memory.peek(self.processor.get_16bit_reg('hl')), self.bit_pos)

    def t_states(self):
        pass

    def __str__(self):
        return 'bit {}, (hl)'.format(self.bit_pos)


def bit_indexed_indirect(processor, memory, reg, offset, bit_pos):
    address = processor.index_registers[reg] + offset
    _bit(processor, memory.peek(address), bit_pos)


def _bit(processor, value, bit_pos):
    processor.set_condition('z', value & pow(2, bit_pos) == 0)
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
        pass

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
        self.memory.poke(address, _res(self.memory.peek(address), self.bit_pos))

    def t_states(self):
        pass

    def __str__(self):
        return 'res {}, (hl)'.format(self.bit_pos)


def res_indexed_indirect(processor, memory, reg, offset, bit_pos):
    address = processor.index_registers[reg] + offset
    memory.poke(address, _res(memory.peek(address), bit_pos))


def _res(value, bit_pos):
    return value & (0xff - pow(2, bit_pos))


def set_reg(processor, reg, bit_pos):
    processor.main_registers[reg] = _set(processor.main_registers[reg], bit_pos)


def set_hl_indirect(processor, memory, bit_pos):
    address = processor.get_16bit_reg('hl')
    memory.poke(address, _set(memory.peek(address), bit_pos))


def set_indexed_indirect(processor, memory, reg, offset, bit_pos):
    address = processor.index_registers[reg] + offset
    memory.poke(address, _set(memory.peek(address), bit_pos))


def _set(value, bit_pos):
    return value | pow(2, bit_pos)