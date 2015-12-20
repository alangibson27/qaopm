from z80.baseop import BaseOp
from z80.funcs import to_signed, big_endian_value


class OpJp(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        address = _abs_jp_address(self.processor)
        jp_to(self.processor, address)

    def t_states(self):
        pass

    def __str__(self):
        return 'jp nn'


class OpJpHlIndirect(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        self.processor.special_registers['pc'] = self.processor.get_16bit_reg('hl')

    def t_states(self):
        pass

    def __str__(self):
        return 'jp (hl)'


class OpJpIndexedIndirect(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self):
        self.processor.special_registers['pc'] = self.processor.index_registers[self.reg]

    def t_states(self):
        pass

    def __str__(self):
        return 'jp ({})'.format(self.reg)


class OpJpNz(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        _cond_jp(self.processor, 'z', False)

    def t_states(self):
        pass

    def __str__(self):
        return 'jp nz, nn'


class OpJpZ(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        _cond_jp(self.processor, 'z', True)

    def t_states(self):
        pass

    def __str__(self):
        return 'jp z, nn'


class OpJpNc(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        _cond_jp(self.processor, 'c', False)

    def t_states(self):
        pass

    def __str__(self):
        return 'jp nc, nn'


class OpJpC(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        _cond_jp(self.processor, 'c', True)

    def t_states(self):
        pass

    def __str__(self):
        return 'jp c, nn'


class OpJpPo(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        _cond_jp(self.processor, 'p', False)

    def t_states(self):
        pass

    def __str__(self):
        return 'jp po, nn'


class OpJpPe(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        _cond_jp(self.processor, 'p', True)

    def t_states(self):
        pass

    def __str__(self):
        return 'jp pe, nn'


class OpJpP(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        _cond_jp(self.processor, 's', False)

    def t_states(self):
        pass

    def __str__(self):
        return 'jp p, nn'


class OpJpM(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        _cond_jp(self.processor, 's', True)

    def t_states(self):
        pass

    def __str__(self):
        return 'jp m, nn'


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


def jp_to(processor, address):
    processor.special_registers['pc'] = address


def _cond_jr(processor, flag, jump_value):
    offset = to_signed(processor.get_next_byte())
    if processor.condition(flag) == jump_value:
        _jr_offset(processor, offset)


def _jr_offset(processor, offset):
    processor.special_registers['pc'] = (processor.special_registers['pc'] + offset) & 0xffff


