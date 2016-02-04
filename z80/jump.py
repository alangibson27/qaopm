from z80.baseop import BaseOp
from z80.funcs import to_signed, big_endian_value


class OpJp(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        address = big_endian_value([instruction_bytes.pop(), instruction_bytes.pop()])
        jp_to(self.processor, address)
        return 10, True

    def __str__(self):
        return 'jp nn'


class OpJpHlIndirect(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        self.processor.special_registers['pc'] = self.processor.get_16bit_reg('hl')
        return 4, True

    def __str__(self):
        return 'jp (hl)'


class OpJpIndexedIndirect(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self, instruction_bytes):
        self.processor.special_registers['pc'] = self.processor.index_registers[self.reg]
        return 8, True

    def __str__(self):
        return 'jp ({})'.format(self.reg)


class OpJpNz(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        return _cond_jp(self.processor, instruction_bytes, 'z', False)

    def __str__(self):
        return 'jp nz, nn'


class OpJpZ(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        return _cond_jp(self.processor, instruction_bytes, 'z', True)

    def __str__(self):
        return 'jp z, nn'


class OpJpNc(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        return _cond_jp(self.processor, instruction_bytes, 'c', False)

    def __str__(self):
        return 'jp nc, nn'


class OpJpC(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        return _cond_jp(self.processor, instruction_bytes, 'c', True)

    def __str__(self):
        return 'jp c, nn'


class OpJpPo(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        return _cond_jp(self.processor, instruction_bytes, 'p', False)

    def __str__(self):
        return 'jp po, nn'


class OpJpPe(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        return _cond_jp(self.processor, instruction_bytes, 'p', True)

    def __str__(self):
        return 'jp pe, nn'


class OpJpP(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        return _cond_jp(self.processor, instruction_bytes, 's', False)

    def __str__(self):
        return 'jp p, nn'


class OpJpM(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        return _cond_jp(self.processor, instruction_bytes, 's', True)

    def __str__(self):
        return 'jp m, nn'


def _cond_jp(processor, instruction_bytes, flag, jump_value):
    address = big_endian_value([instruction_bytes.pop(), instruction_bytes.pop()])
    if processor.condition(flag) == jump_value:
        processor.special_registers['pc'] = address
        return 10, True
    else:
        return 10, False


class OpJr(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        _jr_offset(self.processor.special_registers, to_signed(instruction_bytes.pop()))
        return 12, True

    def __str__(self):
        return 'jr n'


class OpJrC(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        return _cond_jr(self.processor, instruction_bytes, 'c', True)

    def __str__(self):
        return 'jr c, n'


class OpJrNc(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        return _cond_jr(self.processor, instruction_bytes, 'c', False)

    def __str__(self):
        return 'jr nc, n'


class OpJrZ(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        return _cond_jr(self.processor, instruction_bytes, 'z', True)

    def __str__(self):
        return 'jr z, n'


class OpJrNz(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        return _cond_jr(self.processor, instruction_bytes, 'z', False)

    def __str__(self):
        return 'jr nz, n'


class OpDjnz(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        offset = to_signed(instruction_bytes.pop())
        self.processor.main_registers['b'] = (self.processor.main_registers['b'] - 1) & 0xff
        if self.processor.main_registers['b'] != 0:
            _jr_offset(self.processor.special_registers, offset)
            return 13, True
        else:
            return 8, False

    def __str__(self):
        return 'djnz n'


def jp_to(processor, address):
    processor.special_registers['pc'] = address


def _cond_jr(processor, instruction_bytes, flag, jump_value):
    offset = to_signed(instruction_bytes.pop())
    if processor.condition(flag) == jump_value:
        _jr_offset(processor.special_registers, offset)
        return 12, True
    else:
        return 7, False


def _jr_offset(special_registers, offset):
    special_registers['pc'] = (special_registers['pc'] + (offset + 2)) & 0xffff
