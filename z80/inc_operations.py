from baseop import BaseOp
from funcs import bitwise_add, bitwise_sub, to_signed


class OpInc8Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self):
        self.processor.main_registers[self.reg] = _inc_value(self.processor, self.processor.main_registers[self.reg])

    def t_states(self):
        pass

    def __str__(self):
        return 'inc {}'.format(self.reg)


class OpDec8Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self):
        self.processor.main_registers[self.reg] = _dec_value(self.processor, self.processor.main_registers[self.reg])

    def t_states(self):
        pass

    def __str__(self):
        return 'dec {}'.format(self.reg)


class OpInc16Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self):
        result = (self.processor.get_16bit_reg(self.reg) + 1) & 0xffff
        self.processor.set_16bit_reg(self.reg, result)

    def t_states(self):
        return 6

    def __str__(self):
        return 'inc {}'.format(self.reg)


class OpDec16Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self):
        result = (self.processor.get_16bit_reg(self.reg) - 1) & 0xffff
        self.processor.set_16bit_reg(self.reg, result)

    def t_states(self):
        pass

    def __str__(self):
        return 'dec {}'.format(self.reg)


class OpIncHlIndirect(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        address = self.processor.get_16bit_reg('hl')
        result = _inc_value(self.processor, self.memory.peek(address))
        self.memory.poke(address, result)

    def t_states(self):
        pass

    def __str__(self):
        return 'inc (hl)'


class OpDecHlIndirect(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        address = self.processor.get_16bit_reg('hl')
        result = _dec_value(self.processor, self.memory.peek(address))
        self.memory.poke(address, result)

    def t_states(self):
        pass

    def __str__(self):
        return 'dec (hl)'


class OpIncIndexed(BaseOp):
    def __init__(self, processor, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.indexed_reg = indexed_reg

    def execute(self):
        result = (self.processor.index_registers[self.indexed_reg] + 1) & 0xffff
        self.processor.index_registers[self.indexed_reg] = result

    def t_states(self):
        pass

    def __str__(self):
        return 'inc {}'.format(self.indexed_reg)


class OpDecIndexed(BaseOp):
    def __init__(self, processor, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.indexed_reg = indexed_reg

    def execute(self):
        result = (self.processor.index_registers[self.indexed_reg] - 1) & 0xffff
        self.processor.index_registers[self.indexed_reg] = result

    def t_states(self):
        pass

    def __str__(self):
        return 'dec {}'.format(self.indexed_reg)


class OpIncIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self):
        offset = to_signed(self.processor.get_next_byte())
        address = self.processor.index_registers[self.indexed_reg] + offset
        result = _inc_value(self.processor, self.memory.peek(address))
        self.memory.poke(address, result)

    def t_states(self):
        pass

    def __str__(self):
        return 'inc ({} + d)'.format(self.indexed_reg)


class OpDecIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self):
        offset = to_signed(self.processor.get_next_byte())
        address = self.processor.index_registers[self.indexed_reg] + offset
        result = _dec_value(self.processor, self.memory.peek(address))
        self.memory.poke(address, result)

    def t_states(self):
        pass

    def __str__(self):
        return 'inc ({} + d)'.format(self.indexed_reg)


def _inc_value(processor, value):
    processor.set_condition('p', value == 0x7f)
    result, half_carry, _ = bitwise_add(value, 1)

    processor.set_condition('s', to_signed(result) < 0)
    processor.set_condition('z', result == 0)
    processor.set_condition('h', half_carry)
    processor.set_condition('n', False)
    return result


def _dec_value(processor, value):
    processor.set_condition('p', value == 0x80)
    result, half_carry, _ = bitwise_sub(value, 1)

    processor.set_condition('s', to_signed(result) < 0)
    processor.set_condition('z', result == 0)
    processor.set_condition('h', half_carry)
    processor.set_condition('n', True)
    return result
