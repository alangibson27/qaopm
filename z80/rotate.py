from baseop import BaseOp
from funcs import has_parity, to_hex_digits


class OpRlca(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        result = _rlc_value(self.processor, self.processor.main_registers['a'])
        self.processor.main_registers['a'] = result

    def t_states(self):
        pass

    def __str__(self):
        return 'rlca'


class OpRla(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        value = self.processor.main_registers['a']
        rotated = _rl_value(self.processor, value)
        self.processor.main_registers['a'] = rotated

    def t_states(self):
        pass

    def __str__(self):
        return 'rla'


class OpRrca(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        value = self.processor.main_registers['a']
        rotated = _rrc_value(self.processor, value)
        self.processor.main_registers['a'] = rotated

    def t_states(self):
        pass

    def __str__(self):
        return 'rrca'


class OpRra(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        low_bit = self.processor.main_registers['a'] & 0b1
        rotated = self.processor.main_registers['a'] >> 1
        if self.processor.condition('c'):
            rotated |= 0b10000000

        self.processor.main_registers['a'] = rotated
        self.processor.set_condition('c', low_bit == 1)
        self.processor.set_condition('h', False)
        self.processor.set_condition('n', False)

    def t_states(self):
        pass

    def __str__(self):
        return 'rra'


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


def rld(processor, memory):
    address = processor.get_16bit_reg('hl')
    mem_value = memory.peek(address)
    mem_digits = to_hex_digits(mem_value)

    reg_value = processor.main_registers['a']
    reg_digits = to_hex_digits(reg_value)

    memory.poke(address, (mem_digits[1] << 4) + reg_digits[1])
    processor.main_registers['a'] = reg_digits[0] + (mem_digits[0] >> 4)

    _set_sign_zero_parity_flags(processor, processor.main_registers['a'])
    processor.set_condition('h', False)
    processor.set_condition('n', False)


def rrd(processor, memory):
    address = processor.get_16bit_reg('hl')
    mem_value = memory.peek(address)
    mem_digits = to_hex_digits(mem_value)

    reg_value = processor.main_registers['a']
    reg_digits = to_hex_digits(reg_value)

    memory.poke(address, (reg_digits[1] << 4) + (mem_digits[0] >> 4))
    processor.main_registers['a'] = reg_digits[0] + mem_digits[1]

    _set_sign_zero_parity_flags(processor, processor.main_registers['a'])
    processor.set_condition('h', False)
    processor.set_condition('n', False)


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
