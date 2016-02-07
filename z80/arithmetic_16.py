from baseop import BaseOp
from funcs import *


class OpAddHl16Reg(BaseOp):
    def __init__(self, processor, source_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.source_reg = source_reg

    def execute(self, processor, memory, pc):
        result, half_carry, full_carry = bitwise_add_16bit(processor.get_16bit_reg('hl'),
                                                           processor.get_16bit_reg(self.source_reg))
        processor.set_16bit_reg('hl', result)
        processor.set_condition('h', half_carry)
        processor.set_condition('n', False)
        processor.set_condition('c', full_carry)
        return 11, False, pc

    def __str__(self):
        return 'add hl, {}'.format(self.source_reg)


class OpAdcHl16Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self, processor, memory, pc):
        signed_hl = to_signed_16bit(self.processor.get_16bit_reg('hl'))
        to_add = (self.processor.get_16bit_reg(self.reg) + (1 if self.processor.condition('c') else 0)) & 0xffff
        result, half_carry, full_carry = bitwise_add_16bit(self.processor.get_16bit_reg('hl'), to_add)
        signed_result = to_signed_16bit(result)

        processor.set_16bit_reg('hl', result)
        processor.set_condition('s', result & 0x8000 > 0)
        processor.set_condition('z', result == 0)
        processor.set_condition('h', half_carry)
        processor.set_condition('p', (signed_hl < 0) != (signed_result < 0))
        processor.set_condition('n', False)
        processor.set_condition('c', full_carry)
        return 15, False, pc

    def __str__(self):
        return 'adc hl, {}'.format(self.reg)


class OpSbcHl16Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self, processor, memory, pc):
        signed_hl = to_signed_16bit(self.processor.get_16bit_reg('hl'))
        to_sub = (self.processor.get_16bit_reg(self.reg) + (1 if self.processor.condition('c') else 0)) & 0xffff
        result, half_borrow, full_borrow = bitwise_sub_16bit(self.processor.get_16bit_reg('hl'), to_sub)
        signed_result = to_signed_16bit(result)

        processor = self.processor
        processor.set_16bit_reg('hl', result)
        processor.set_condition('s', result & 0x8000 > 0)
        processor.set_condition('z', result == 0)
        processor.set_condition('h', half_borrow)
        processor.set_condition('p', (signed_hl < 0) != (signed_result < 0))
        processor.set_condition('n', True)
        processor.set_condition('c', full_borrow)
        return 15, False, pc

    def __str__(self):
        return 'sbc hl, {}'.format(self.reg)


class OpAddIndexedReg(BaseOp):
    def __init__(self, processor, indexed_reg, source_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.indexed_reg = indexed_reg
        self.source_reg = source_reg

    def execute(self, processor, memory, pc):
        result, half_carry, full_carry = bitwise_add_16bit(processor.index_registers[self.indexed_reg],
                                                           processor.get_16bit_reg(self.source_reg))

        processor.index_registers[self.indexed_reg] = result
        processor.set_condition('h', half_carry)
        processor.set_condition('n', False)
        processor.set_condition('c', full_carry)
        return 15, False, pc

    def __str__(self):
        return 'add {}, {}'.format(self.indexed_reg, self.source_reg)


def inc_16reg(processor, reg_pair):
    result = (processor.get_16bit_reg(reg_pair) + 1) & 0xffff
    processor.set_16bit_reg(reg_pair, result)


def dec_16reg(processor, reg_pair):
    result = (processor.get_16bit_reg(reg_pair) - 1) & 0xffff
    processor.set_16bit_reg(reg_pair, result)


