from z80.funcs import big_endian_value


def jp(processor):
    address = _abs_jp_address(processor)
    processor.special_registers['pc'] = address


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
    return big_endian_value([processor.get_value_at_pc(), processor.get_value_at_pc()])