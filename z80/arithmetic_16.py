from funcs import *


def add_hl_reg(processor, reg_pair):
    result, half_carry, full_carry = bitwise_add_16bit(processor.get_16bit_reg('hl'), processor.get_16bit_reg(reg_pair))
    processor.set_16bit_reg('hl', result)

    processor.set_condition('h', half_carry)
    processor.set_condition('n', False)
    processor.set_condition('c', full_carry)


def adc_hl_reg(processor, reg_pair):
    signed_hl = to_signed_16bit(processor.get_16bit_reg('hl'))
    to_add = (processor.get_16bit_reg(reg_pair) + (1 if processor.condition('c') else 0)) & 0xffff
    result, half_carry, full_carry = bitwise_add_16bit(processor.get_16bit_reg('hl'), to_add)
    signed_result = to_signed_16bit(result)

    processor.set_16bit_reg('hl', result)
    processor.set_condition('s', result & 0x8000 > 0)
    processor.set_condition('z', result == 0)
    processor.set_condition('h', half_carry)
    processor.set_condition('p', (signed_hl < 0) != (signed_result < 0))
    processor.set_condition('n', False)
    processor.set_condition('c', full_carry)


def sbc_hl_reg(processor, reg_pair):
    signed_hl = to_signed_16bit(processor.get_16bit_reg('hl'))
    to_sub = (processor.get_16bit_reg(reg_pair) + (1 if processor.condition('c') else 0)) & 0xffff
    result, half_borrow, full_borrow = bitwise_sub_16bit(processor.get_16bit_reg('hl'), to_sub)
    signed_result = to_signed_16bit(result)

    processor.set_16bit_reg('hl', result)
    processor.set_condition('s', result & 0x8000 > 0)
    processor.set_condition('z', result == 0)
    processor.set_condition('h', half_borrow)
    processor.set_condition('p', (signed_hl < 0) != (signed_result < 0))
    processor.set_condition('n', True)
    processor.set_condition('c', full_borrow)


def add_indexed_reg(processor, indexed_reg, reg_pair):
    result, half_carry, full_carry = bitwise_add_16bit(processor.index_registers[indexed_reg],
                                                       processor.get_16bit_reg(reg_pair))

    processor.index_registers[indexed_reg] = result
    processor.set_condition('h', half_carry)
    processor.set_condition('n', False)
    processor.set_condition('c', full_carry)


def inc_16reg(processor, reg_pair):
    result = (processor.get_16bit_reg(reg_pair) + 1) & 0xffff
    processor.set_16bit_reg(reg_pair, result)


def inc_indexed_reg(processor, reg):
    result = (processor.index_registers[reg] + 1) & 0xffff
    processor.index_registers[reg] = result


def dec_16reg(processor, reg_pair):
    result = (processor.get_16bit_reg(reg_pair) - 1) & 0xffff
    processor.set_16bit_reg(reg_pair, result)


def dec_indexed_reg(processor, reg):
    result = (processor.index_registers[reg] - 1) & 0xffff
    processor.index_registers[reg] = result
