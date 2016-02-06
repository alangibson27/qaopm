from memory.memory import fetch_word, fetch_signed_byte
from z80.baseop import BaseOp


class OpJp(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        address, pc = fetch_word(memory, pc)
        jp_to(self.processor, address)
        return 10, True, pc

    def __str__(self):
        return 'jp nn'


class OpJpHlIndirect(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        self.processor.special_registers['pc'] = self.processor.get_16bit_reg('hl')
        return 4, True, pc

    def __str__(self):
        return 'jp (hl)'


class OpJpIndexedIndirect(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self, processor, memory, pc):
        self.processor.special_registers['pc'] = self.processor.index_registers[self.reg]
        return 8, True, pc

    def __str__(self):
        return 'jp ({})'.format(self.reg)


class OpJpNz(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        return _cond_jp(processor, memory, pc, 'z', False)

    def __str__(self):
        return 'jp nz, nn'


class OpJpZ(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        return _cond_jp(processor, memory, pc, 'z', True)

    def __str__(self):
        return 'jp z, nn'


class OpJpNc(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        return _cond_jp(processor, memory, pc, 'c', False)

    def __str__(self):
        return 'jp nc, nn'


class OpJpC(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        return _cond_jp(processor, memory, pc, 'c', True)

    def __str__(self):
        return 'jp c, nn'


class OpJpPo(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        return _cond_jp(processor, memory, pc, 'p', False)

    def __str__(self):
        return 'jp po, nn'


class OpJpPe(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        return _cond_jp(processor, memory, pc, 'p', True)

    def __str__(self):
        return 'jp pe, nn'


class OpJpP(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        return _cond_jp(processor, memory, pc, 's', False)

    def __str__(self):
        return 'jp p, nn'


class OpJpM(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        return _cond_jp(processor, memory, pc, 's', True)

    def __str__(self):
        return 'jp m, nn'


def _cond_jp(processor, memory, pc, flag, jump_value):
    address, pc = fetch_word(memory, pc)
    if processor.condition(flag) == jump_value:
        processor.special_registers['pc'] = address
        return 10, True, pc
    else:
        return 10, False, pc


class OpJr(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        offset, pc = fetch_signed_byte(memory, pc)
        _jr_offset(processor.special_registers, offset)
        return 12, True, pc

    def __str__(self):
        return 'jr n'


class OpJrC(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        return _cond_jr(processor, memory, pc, 'c', True)

    def __str__(self):
        return 'jr c, n'


class OpJrNc(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        return _cond_jr(processor, memory, pc, 'c', False)

    def __str__(self):
        return 'jr nc, n'


class OpJrZ(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        return _cond_jr(processor, memory, pc, 'z', True)

    def __str__(self):
        return 'jr z, n'


class OpJrNz(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        return _cond_jr(processor, memory, pc, 'z', False)

    def __str__(self):
        return 'jr nz, n'


class OpDjnz(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        offset, pc = fetch_signed_byte(memory, pc)
        self.processor.main_registers['b'] = (self.processor.main_registers['b'] - 1) & 0xff
        if self.processor.main_registers['b'] != 0:
            _jr_offset(self.processor.special_registers, offset)
            return 13, True, pc
        else:
            return 8, False, pc

    def __str__(self):
        return 'djnz n'


def jp_to(processor, address):
    processor.special_registers['pc'] = address


def _cond_jr(processor, memory, pc, flag, jump_value):
    offset, pc = fetch_signed_byte(memory, pc)
    if processor.condition(flag) == jump_value:
        _jr_offset(processor.special_registers, offset)
        return 12, True, pc
    else:
        return 7, False, pc


def _jr_offset(special_registers, offset):
    special_registers['pc'] = (special_registers['pc'] + (offset + 2)) & 0xffff
