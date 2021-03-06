from baseop import BaseOp
from z80.funcs import bitwise_sub


class OpLdi(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self, processor, memory, pc):
        _block_transfer(self.processor, self.memory, 1)
        return 16, False, pc

    def __str__(self):
        return 'ldi'


class OpLdd(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self, processor, memory, pc):
        _block_transfer(self.processor, self.memory, -1)
        return 16, False, pc

    def __str__(self):
        return 'ldd'


class OpCpi(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self, processor, memory, pc):
        _block_compare(self.processor, self.memory, 1)
        return 16, False, pc

    def __str__(self):
        return 'cpi'


class OpCpd(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self, processor, memory, pc):
        _block_compare(self.processor, self.memory, -1)
        return 16, False, pc

    def __str__(self):
        return 'cpd'


class BlockOp(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor
        self.last_t_states = None

    def _decrement_bc_and_update_pc(self, pc):
        bc = self.processor.get_16bit_reg('bc')
        if not bc == 0x0000:
            self.processor.special_registers['pc'] = (self.processor.special_registers['pc']) % 0x10000
        return (16, False, pc) if bc == 0x0000 else (21, True, pc)


class OpLdir(BlockOp):
    def __init__(self, processor, memory):
        BlockOp.__init__(self, processor)
        self.memory = memory

    def execute(self, processor, memory, pc):
        _block_transfer(self.processor, self.memory, 1)
        self.processor.set_condition('p', False)
        return self._decrement_bc_and_update_pc(pc)

    def __str__(self):
        return 'ldir'


class OpLddr(BlockOp):
    def __init__(self, processor, memory):
        BlockOp.__init__(self, processor)
        self.memory = memory

    def execute(self, processor, memory, pc):
        _block_transfer(self.processor, self.memory, -1)
        self.processor.set_condition('p', False)
        return self._decrement_bc_and_update_pc(pc)

    def __str__(self):
        return 'lddr'


class OpCpir(BlockOp):
    def __init__(self, processor, memory):
        BlockOp.__init__(self, processor)
        self.memory = memory

    def execute(self, processor, memory, pc):
        _block_compare(self.processor, self.memory, 1)
        return self._decrement_bc_and_update_pc(pc)

    def __str__(self):
        return 'cpir'


class OpCpdr(BlockOp):
    def __init__(self, processor, memory):
        BlockOp.__init__(self, processor)
        self.memory = memory

    def execute(self, processor, memory, pc):
        _block_compare(self.processor, self.memory, -1)
        return self._decrement_bc_and_update_pc(pc)

    def __str__(self):
        return 'cpdr'


def _block_transfer(processor, memory, increment):
    src_addr = processor.get_16bit_reg('hl')
    tgt_addr = processor.get_16bit_reg('de')

    memory[0xffff & tgt_addr] = memory[src_addr]

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

    value_to_compare = memory[src_addr]
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
