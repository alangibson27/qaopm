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
