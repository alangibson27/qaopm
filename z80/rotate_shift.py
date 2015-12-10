from funcs import has_parity


def rlca(processor):
    _rlc(processor, 'a')


def rla(processor):
    high_bit = processor.main_registers['a'] >> 7
    rotated = (processor.main_registers['a'] << 1) & 0xff
    if processor.condition('c'):
        rotated |= 0b1

    processor.main_registers['a'] = rotated
    processor.set_condition('c', high_bit == 1)
    processor.set_condition('h', False)
    processor.set_condition('n', False)


def rrca(processor):
    low_bit = processor.main_registers['a'] & 0b1
    rotated = processor.main_registers['a'] >> 1
    if low_bit > 0:
        rotated |= 0b10000000

    processor.main_registers['a'] = rotated
    processor.set_condition('c', low_bit == 1)
    processor.set_condition('h', False)
    processor.set_condition('n', False)


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
    result = _rlc(processor, reg)
    processor.set_condition('s', result & 0b10000000 > 0)
    processor.set_condition('z', result == 0)
    processor.set_condition('p', has_parity(result))


def _rlc(processor, reg):
    high_bit = processor.main_registers[reg] >> 7
    rotated = (processor.main_registers[reg] << 1) & 0xff
    rotated |= high_bit
    processor.main_registers[reg] = rotated
    processor.set_condition('c', high_bit == 1)
    processor.set_condition('h', False)
    processor.set_condition('n', False)
    return rotated

