from funcs import big_endian_value


def call(processor):
    _call(processor, _get_destination_from_pc(processor))


def rst(processor, jump_address):
    _call(processor, jump_address)


def call_nz(processor):
    address = _get_destination_from_pc(processor)
    if not processor.condition('z'):
        _call(processor, address)


def call_z(processor):
    address = _get_destination_from_pc(processor)
    if processor.condition('z'):
        _call(processor, address)


def call_nc(processor):
    address = _get_destination_from_pc(processor)
    if not processor.condition('c'):
        _call(processor, address)


def call_c(processor):
    address = _get_destination_from_pc(processor)
    if processor.condition('c'):
        _call(processor, address)


def call_po(processor):
    address = _get_destination_from_pc(processor)
    if not processor.condition('p'):
        _call(processor, address)


def call_pe(processor):
    address = _get_destination_from_pc(processor)
    if processor.condition('p'):
        _call(processor, address)


def call_p(processor):
    address = _get_destination_from_pc(processor)
    if not processor.condition('s'):
        _call(processor, address)


def call_m(processor):
    address = _get_destination_from_pc(processor)
    if processor.condition('s'):
        _call(processor, address)


def _call(processor, destination):
    sp_high = processor.special_registers['pc'] >> 8
    sp_low = processor.special_registers['pc'] & 0xff
    processor.push_byte(sp_high)
    processor.push_byte(sp_low)
    processor.special_registers['pc'] = destination


def _get_destination_from_pc(processor):
    next_pc_low = processor.get_value_at_pc()
    next_pc_high = processor.get_value_at_pc()
    return big_endian_value([next_pc_low, next_pc_high])


def ret(processor):
    processor.special_registers['pc'] = _get_destination_from_stack(processor)


def ret_nz(processor):
    if not processor.condition('z'):
        processor.special_registers['pc'] = _get_destination_from_stack(processor)


def ret_z(processor):
    if processor.condition('z'):
        processor.special_registers['pc'] = _get_destination_from_stack(processor)


def ret_nc(processor):
    if not processor.condition('c'):
        processor.special_registers['pc'] = _get_destination_from_stack(processor)


def ret_c(processor):
    if processor.condition('c'):
        processor.special_registers['pc'] = _get_destination_from_stack(processor)


def ret_po(processor):
    if not processor.condition('p'):
        processor.special_registers['pc'] = _get_destination_from_stack(processor)


def ret_pe(processor):
    if processor.condition('p'):
        processor.special_registers['pc'] = _get_destination_from_stack(processor)


def ret_p(processor):
    if not processor.condition('s'):
        processor.special_registers['pc'] = _get_destination_from_stack(processor)


def ret_m(processor):
    if processor.condition('s'):
        processor.special_registers['pc'] = _get_destination_from_stack(processor)


def _get_destination_from_stack(processor):
    return big_endian_value([processor.pop_byte(), processor.pop_byte()])
