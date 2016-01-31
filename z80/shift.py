from baseop import BaseOp
from funcs import has_parity


class OpSlaReg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self):
        result = _sla_value(self.processor, self.processor.main_registers[self.reg])
        self.processor.main_registers[self.reg] = result
        return 8

    def __str__(self):
        return 'sla {}'.format(self.reg)


class OpSlaHlIndirect(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        address = self.processor.get_16bit_reg('hl')
        result = _sla_value(self.processor, self.memory[0xffff & address])
        self.memory[address] = result
        return 15

    def __str__(self):
        return 'sla (hl)'


class OpSllReg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self):
        result = _sll_value(self.processor, self.processor.main_registers[self.reg])
        self.processor.main_registers[self.reg] = result
        return 8

    def __str__(self):
        return 'sll {}'.format(self.reg)


class OpSllHlIndirect(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        address = self.processor.get_16bit_reg('hl')
        result = _sll_value(self.processor, self.memory[0xffff & address])
        self.memory[address] = result
        return 15

    def __str__(self):
        return 'sll (hl)'


class OpSraReg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self):
        result = _sra_value(self.processor, self.processor.main_registers[self.reg])
        self.processor.main_registers[self.reg] = result
        return 8

    def __str__(self):
        return 'sra {}'.format(self.reg)


class OpSraHlIndirect(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        address = self.processor.get_16bit_reg('hl')
        result = _sra_value(self.processor, self.memory[0xffff & address])
        self.memory[address] = result
        return 15

    def __str__(self):
        return 'sra (hl)'


class OpSrlReg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self):
        result = _srl_value(self.processor, self.processor.main_registers[self.reg])
        self.processor.main_registers[self.reg] = result
        return 8

    def __str__(self):
        return 'srl {}'.format(self.reg)


class OpSrlHlIndirect(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        address = self.processor.get_16bit_reg('hl')
        result = _srl_value(self.processor, self.memory[0xffff & address])
        self.memory[address] = result
        return 15

    def __str__(self):
        return 'srl (hl)'


class OpSlaIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self):
        offset = self.processor.get_signed_offset_byte()
        address = self.processor.index_registers[self.indexed_reg] + offset
        value = self.memory[0xffff & address]
        result = _sla_value(self.processor, value)
        self.memory[address] = result
        return 23

    def __str__(self):
        return 'sla ({} + d)'.format(self.indexed_reg)


class OpSraIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self):
        offset = self.processor.get_signed_offset_byte()
        address = self.processor.index_registers[self.indexed_reg] + offset
        value = self.memory[0xffff & address]
        result = _sra_value(self.processor, value)
        self.memory[address] = result
        return 23

    def __str__(self):
        return 'sra ({} + d)'.format(self.indexed_reg)


class OpSrlIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self):
        offset = self.processor.get_signed_offset_byte()
        address = self.processor.index_registers[self.indexed_reg] + offset
        value = self.memory[0xffff & address]
        result = _srl_value(self.processor, value)
        self.memory[address] = result
        return 23

    def __str__(self):
        return 'srl ({} + d)'.format(self.indexed_reg)


def _sla_value(processor, value):
    carry = value >> 7
    rotated = (value << 1) & 0xff
    _set_flags(processor, rotated, carry)
    return rotated


def _sra_value(processor, value):
    carry = value & 0b1
    high_bit = value & 0b10000000
    rotated = value >> 1
    rotated |= high_bit
    _set_flags(processor, rotated, carry)
    return rotated


def _srl_value(processor, value):
    carry = value & 0b1
    rotated = value >> 1
    _set_flags(processor, rotated, carry)
    return rotated


def _sll_value(processor, value):
    new_carry = value >> 7
    rotated = ((value << 1) | 0b1) & 0xff
    _set_flags(processor, rotated, new_carry)
    return rotated


def _set_flags(processor, result, carry):
    processor.set_condition('c', carry == 1)
    processor.set_condition('h', False)
    processor.set_condition('n', False)
    processor.set_condition('s', result & 0b10000000 > 0)
    processor.set_condition('z', result == 0)
    processor.set_condition('p', has_parity(result))
