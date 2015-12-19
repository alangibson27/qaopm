from z80.baseop import BaseOp
from z80.funcs import to_signed, big_endian_value


def jp(processor):
    address = _abs_jp_address(processor)
    jp_to(processor, address)


def jp_to(processor, address):
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


class OpJr(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        _jr_offset(self.processor, to_signed(self.processor.get_next_byte()))

    def t_states(self):
        pass

    def __str__(self):
        return 'jr n'


class OpJrC(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        _cond_jr(self.processor, 'c', True)

    def t_states(self):
        pass

    def __str__(self):
        return 'jr c, n'


class OpJrNc(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        _cond_jr(self.processor, 'c', False)

    def t_states(self):
        pass

    def __str__(self):
        return 'jr nc, n'


class OpJrZ(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        _cond_jr(self.processor, 'z', True)

    def t_states(self):
        pass

    def __str__(self):
        return 'jr z, n'


class OpJrNz(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        _cond_jr(self.processor, 'z', False)

    def t_states(self):
        pass

    def __str__(self):
        return 'jr nz, n'


class OpDjnz(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        offset = to_signed(self.processor.get_next_byte())
        self.processor.main_registers['b'] = (self.processor.main_registers['b'] - 1)
        if self.processor.main_registers['b'] != 0:
            _jr_offset(self.processor, offset)

    def t_states(self):
        pass

    def __str__(self):
        return 'djnz n'


def _cond_jr(processor, flag, jump_value):
    offset = to_signed(processor.get_next_byte())
    if processor.condition(flag) == jump_value:
        _jr_offset(processor, offset)


def _jr_offset(processor, offset):
    processor.special_registers['pc'] = (processor.special_registers['pc'] + offset) & 0xffff


