from funcs import has_parity, to_signed


def sla_reg(processor, register):
    result = _sla_value(processor, processor.main_registers[register])
    processor.main_registers[register] = result


def sla_hl_indirect(processor, memory):
    address = processor.get_16bit_reg('hl')
    result = _sla_value(processor, memory.peek(address))
    memory.poke(address, result)


def sla_indexed(processor, memory, register, offset):
    address = processor.index_registers[register] + offset
    value = memory.peek(address)
    result = _sla_value(processor, value)
    memory.poke(address, result)


def _sla_value(processor, value):
    carry = value >> 7
    rotated = (value << 1) & 0xff
    _set_flags(processor, rotated, carry)
    return rotated


def sra_reg(processor, register):
    result = _sra_value(processor, processor.main_registers[register])
    processor.main_registers[register] = result


def sra_hl_indirect(processor, memory):
    address = processor.get_16bit_reg('hl')
    result = _sra_value(processor, memory.peek(address))
    memory.poke(address, result)


def sra_indexed(processor, memory, register, offset):
    address = processor.index_registers[register] + offset
    value = memory.peek(address)
    result = _sra_value(processor, value)
    memory.poke(address, result)


def _sra_value(processor, value):
    carry = value & 0b1
    high_bit = value & 0b10000000
    rotated = value >> 1
    rotated |= high_bit
    _set_flags(processor, rotated, carry)
    return rotated


def _set_flags(processor, result, carry):
    processor.set_condition('c', carry == 1)
    processor.set_condition('h', False)
    processor.set_condition('n', False)
    processor.set_condition('s', result & 0b10000000 > 0)
    processor.set_condition('z', result == 0)
    processor.set_condition('p', has_parity(result))
