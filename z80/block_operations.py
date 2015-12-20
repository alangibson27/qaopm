from baseop import BaseOp
from z80.funcs import bitwise_sub


class OpLdi(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        _block_transfer(self.processor, self.memory, 1)

    def t_states(self):
        pass

    def __str__(self):
        return 'ldi'


class OpLdd(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        _block_transfer(self.processor, self.memory, -1)

    def t_states(self):
        pass

    def __str__(self):
        return 'ldd'


class OpCpi(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        _block_compare(self.processor, self.memory, 1)

    def t_states(self):
        pass

    def __str__(self):
        return 'cpi'


class OpCpd(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        _block_compare(self.processor, self.memory, -1)

    def t_states(self):
        pass

    def __str__(self):
        return 'cpd'


class OpLdir(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        _block_transfer(self.processor, self.memory, 1)
        self.processor.set_condition('p', False)
        if not (self.processor.main_registers['b'] == 0x00 and self.processor.main_registers['c'] == 0x00):
            self.processor.special_registers['pc'] = (self.processor.special_registers['pc'] - 2) % 0x10000

    def t_states(self):
        pass

    def __str__(self):
        return 'ldir'


class OpLddr(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        _block_transfer(self.processor, self.memory, -1)
        self.processor.set_condition('p', False)
        if not (self.processor.main_registers['b'] == 0x00 and self.processor.main_registers['c'] == 0x00):
            self.processor.special_registers['pc'] = (self.processor.special_registers['pc'] - 2) % 0x10000

    def t_states(self):
        pass

    def __str__(self):
        return 'lddr'


class OpCpir(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        _block_compare(self.processor, self.memory, 1)
        if not (self.processor.get_16bit_reg('bc') == 0x0000):
            self.processor.special_registers['pc'] = (self.processor.special_registers['pc'] - 2) % 0x10000

    def t_states(self):
        pass

    def __str__(self):
        return 'cpir'


class OpCpdr(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        _block_compare(self.processor, self.memory, -1)
        if not (self.processor.get_16bit_reg('bc') == 0x0000):
            self.processor.special_registers['pc'] = (self.processor.special_registers['pc'] - 2) % 0x10000

    def t_states(self):
        pass

    def __str__(self):
        return 'cpdr'


def _block_transfer(processor, memory, increment):
    src_addr = processor.get_16bit_reg('hl')
    tgt_addr = processor.get_16bit_reg('de')

    memory.poke(tgt_addr, memory.peek(src_addr))

    src_addr = (src_addr + increment) % 0x10000
    processor.set_16bit_reg('hl', src_addr)

    tgt_addr = (tgt_addr + increment) % 0x10000
    processor.set_16bit_reg('de', tgt_addr)

    counter = _decrement_bc(processor)

    processor.set_condition('h', False)
    processor.set_condition('p', counter != 0)
    processor.set_condition('n', False)


def _block_compare(processor, memory, increment):
    src_addr = processor.get_16bit_reg('hl')

    value_to_compare = memory.peek(src_addr)
    result, half_carry, full_carry = bitwise_sub(processor.main_registers['a'], value_to_compare)

    src_addr = (src_addr + increment) % 0x10000
    processor.set_16bit_reg('hl', src_addr)

    new_bc = _decrement_bc(processor)

    processor.set_condition('s', result & 0b10000000 != 0)
    processor.set_condition('z', result == 0)
    processor.set_condition('h', half_carry)
    processor.set_condition('p', new_bc != 0)
    processor.set_condition('n', True)


def _decrement_bc(processor):
    counter = processor.get_16bit_reg('bc')
    counter = (counter - 1) & 0xffff

    processor.set_16bit_reg('bc', counter)
    return counter
