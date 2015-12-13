def bit_reg(processor, reg, bit_pos):
    _bit(processor, processor.main_registers[reg], bit_pos)


def bit_hl_indirect(processor, memory, bit_pos):
    _bit(processor, memory.peek(processor.get_16bit_reg('hl')), bit_pos)


def bit_indexed_indirect(processor, memory, reg, offset, bit_pos):
    address = processor.index_registers[reg] + offset
    _bit(processor, memory.peek(address), bit_pos)


def _bit(processor, value, bit_pos):
    processor.set_condition('z', value & pow(2, bit_pos) == 0)
    processor.set_condition('h', True)
    processor.set_condition('n', False)


def res_reg(processor, reg, bit_pos):
    processor.main_registers[reg] = _res(processor.main_registers[reg], bit_pos)


def res_hl_indirect(processor, memory, bit_pos):
    address = processor.get_16bit_reg('hl')
    memory.poke(address, _res(memory.peek(address), bit_pos))


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