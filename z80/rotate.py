from funcs import has_parity, to_signed


def rlca(processor):
    result = _rlc_value(processor, processor.main_registers['a'])
    processor.main_registers['a'] = result


def rla(processor):
    value = processor.main_registers['a']
    rotated = _rl_value(processor, value)
    processor.main_registers['a'] = rotated


def rrca(processor):
    value = processor.main_registers['a']
    rotated = _rrc_value(processor, value)
    processor.main_registers['a'] = rotated


def rra(processor):
    low_bit = processor.main_registers['a'] & 0b1
    rotated = processor.main_registers['a'] >> 1
    if processor.condition('c'):
        rotated |= 0b10000000

    processor.main_registers['a'] = rotated
    processor.set_condition('c', low_bit == 1)
    processor.set_condition('h', False)
    processor.set_condition('n', False)


def rlc_reg(processor, reg):
    result = _rlc_value(processor, processor.main_registers[reg])
    processor.main_registers[reg] = result
    _set_sign_zero_parity_flags(processor, result)


def rrc_reg(processor, reg):
    result = _rrc_value(processor, processor.main_registers[reg])
    processor.main_registers[reg] = result
    _set_sign_zero_parity_flags(processor, result)


def rrc_hl_indirect(processor, memory):
    address = processor.get_16bit_reg('hl')
    result = _rrc_value(processor, memory.peek(address))
    memory.poke(address, result)
    _set_sign_zero_parity_flags(processor, result)


def rl_reg(processor, reg):
    result = _rl_value(processor, processor.main_registers[reg])
    processor.main_registers[reg] = result
    _set_sign_zero_parity_flags(processor, result)


def rr_reg(processor, reg):
    result = _rr_value(processor, processor.main_registers[reg])
    processor.main_registers[reg] = result
    _set_sign_zero_parity_flags(processor, result)


def rlc_hl_indirect(processor, memory):
    address = processor.get_16bit_reg('hl')
    result = _rlc_value(processor, memory.peek(address))
    memory.poke(address, result)
    _set_sign_zero_parity_flags(processor, result)


def rl_hl_indirect(processor, memory):
    address = processor.get_16bit_reg('hl')
    result = _rl_value(processor, memory.peek(address))
    memory.poke(address, result)
    _set_sign_zero_parity_flags(processor, result)


def rr_hl_indirect(processor, memory):
    address = processor.get_16bit_reg('hl')
    result = _rr_value(processor, memory.peek(address))
    memory.poke(address, result)
    _set_sign_zero_parity_flags(processor, result)


def rlc_indexed(processor, memory, register, offset):
    address = processor.index_registers[register] + offset
    value = memory.peek(address)
    result = _rlc_value(processor, value)
    memory.poke(address, result)
    _set_sign_zero_parity_flags(processor, result)


def rrc_indexed(processor, memory, register, offset):
    address = processor.index_registers[register] + offset
    value = memory.peek(address)
    result = _rrc_value(processor, value)
    memory.poke(address, result)
    _set_sign_zero_parity_flags(processor, result)


def rl_indexed(processor, memory, register, offset):
    address = processor.index_registers[register] + offset
    value = memory.peek(address)
    result = _rl_value(processor, value)
    memory.poke(address, result)
    _set_sign_zero_parity_flags(processor, result)


def rr_indexed(processor, memory, register, offset):
    address = processor.index_registers[register] + offset
    value = memory.peek(address)
    result = _rr_value(processor, value)
    memory.poke(address, result)
    _set_sign_zero_parity_flags(processor, result)


def _rlc_value(processor, value):
    high_bit = value >> 7
    rotated = (value << 1) & 0xff
    rotated |= high_bit
    _set_carry_and_negate_flags_after_left_rotate(processor, high_bit)
    return rotated


def _rl_value(processor, value):
    high_bit = value >> 7
    rotated = (value << 1) & 0xff
    if processor.condition('c'):
        rotated |= 0b1
    _set_carry_and_negate_flags_after_left_rotate(processor, high_bit)
    return rotated


def _rr_value(processor, value):
    low_bit = value & 0b1
    rotated = value >> 1
    if processor.condition('c'):
        rotated |= 0b10000000
    _set_carry_and_negate_flags_after_right_rotate(processor, low_bit)
    return rotated


def _rrc_value(processor, value):
    low_bit = value & 0b1
    rotated = value >> 1
    if low_bit > 0:
        rotated |= 0b10000000
    _set_carry_and_negate_flags_after_right_rotate(processor, low_bit)
    return rotated


def _set_carry_and_negate_flags_after_right_rotate(processor, low_bit):
    processor.set_condition('c', low_bit == 1)
    processor.set_condition('h', False)
    processor.set_condition('n', False)


def _set_carry_and_negate_flags_after_left_rotate(processor, high_bit):
    processor.set_condition('c', high_bit == 1)
    processor.set_condition('h', False)
    processor.set_condition('n', False)


def _set_sign_zero_parity_flags(processor, result):
    processor.set_condition('s', result & 0b10000000 > 0)
    processor.set_condition('z', result == 0)
    processor.set_condition('p', has_parity(result))
