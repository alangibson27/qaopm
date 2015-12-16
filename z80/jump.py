from z80.funcs import to_signed, big_endian_value


def jp(processor):
    address = _abs_jp_address(processor)
    processor.special_registers['pc'] = address


def jp_hl_indirect(processor):
    processor.special_registers['pc'] = processor.get_16bit_reg('hl')


def jp_indexed_indirect(processor, reg):
    processor.special_registers['pc'] = processor.index_registers[reg]


def jp_nz(processor):
    _cond_jp(processor, 'z', False)


def jp_z(processor):
    _cond_jp(processor, 'z', True)


def jp_nc(processor):
    _cond_jp(processor, 'c', False)


def jp_c(processor):
    _cond_jp(processor, 'c', True)


def jp_po(processor):
    _cond_jp(processor, 'p', False)


def jp_pe(processor):
    _cond_jp(processor, 'p', True)


def jp_p(processor):
    _cond_jp(processor, 's', False)


def jp_m(processor):
    _cond_jp(processor, 's', True)


def _cond_jp(processor, flag, jump_value):
    address = _abs_jp_address(processor)
    if processor.condition(flag) == jump_value:
        processor.special_registers['pc'] = address


def _abs_jp_address(processor):
    return big_endian_value([processor.get_next_byte(), processor.get_next_byte()])


def jr(processor):
    _jr_offset(processor, to_signed(processor.get_next_byte()))


def jr_c(processor):
    _cond_jr(processor, 'c', True)


def jr_nc(processor):
    _cond_jr(processor, 'c', False)


def jr_z(processor):
    _cond_jr(processor, 'z', True)


def jr_nz(processor):
    _cond_jr(processor, 'z', False)


def _cond_jr(processor, flag, jump_value):
    offset = to_signed(processor.get_next_byte())
    if processor.condition(flag) == jump_value:
        _jr_offset(processor, offset)


def _jr_offset(processor, offset):
    processor.special_registers['pc'] = (processor.special_registers['pc'] + offset) & 0xffff


def djnz(processor):
    offset = to_signed(processor.get_next_byte())
    processor.main_registers['b'] = (processor.main_registers['b'] - 1)
    if processor.main_registers['b'] != 0:
        _jr_offset(processor, offset)