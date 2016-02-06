from funcs import big_endian_value, high_low_pair
from memory.memory import fetch_word
from z80.baseop import BaseOp


class OpCall(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        word, pc = fetch_word(memory, pc)
        call_to(self.processor, 3, word)
        return 17, True, pc

    def __str__(self):
        return 'call nn'


class OpCallDirect(BaseOp):
    def __init__(self, processor, address, interrupt_triggered = False):
        BaseOp.__init__(self)
        self.processor = processor
        self.address = address
        self.interrupt_triggered = interrupt_triggered

    def execute(self, processor, memory, pc):
        call_to(self.processor, 0 if self.interrupt_triggered else 3, self.address)
        return 17, True, pc

    def __str__(self):
        return 'im2 response'


class OpRst(BaseOp):
    def __init__(self, processor, jump_address, interrupt_triggered = False):
        BaseOp.__init__(self)
        self.processor = processor
        self.jump_address = jump_address
        self.interrupt_triggered = interrupt_triggered

    def execute(self, processor, memory, pc):
        call_to(self.processor, 0 if self.interrupt_triggered else 1, self.jump_address)
        return 11, True, pc

    def __str__(self):
        return 'rst {}'.format(hex(self.jump_address))


class OpCallNz(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        address, pc = fetch_word(memory, pc)
        if not self.processor.condition('z'):
            call_to(self.processor, 3, address)
            return 5, True, pc
        else:
            return 3, False, pc

    def __str__(self):
        return 'call nz, nn'


class OpCallZ(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        address, pc = fetch_word(memory, pc)
        if self.processor.condition('z'):
            call_to(self.processor, 3, address)
            return 5, True, pc
        else:
            return 3, False, pc

    def __str__(self):
        return 'call z, nn'


class OpCallNc(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        address, pc = fetch_word(memory, pc)
        if not self.processor.condition('c'):
            call_to(self.processor, 3, address)
            return 5, True, pc
        else:
            return 3, False, pc

    def __str__(self):
        return 'call nc, nn'


class OpCallC(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        address, pc = fetch_word(memory, pc)
        if self.processor.condition('c'):
            call_to(self.processor, 3, address)
            return 5, True, pc
        else:
            return 3, False, pc

    def __str__(self):
        return 'call c, nn'


class OpCallPo(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        address, pc = fetch_word(memory, pc)
        if not self.processor.condition('p'):
            call_to(self.processor, 3, address)
            return 5, True, pc
        else:
            return 3, False, pc

    def __str__(self):
        return 'call po, nn'


class OpCallPe(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        address, pc = fetch_word(memory, pc)
        if self.processor.condition('p'):
            call_to(self.processor, 3, address)
            return 5, True, pc
        else:
            return 3, False, pc

    def __str__(self):
        return 'call pe, nn'


class OpCallP(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        address, pc = fetch_word(memory, pc)
        if not self.processor.condition('s'):
            call_to(self.processor, 3, address)
            return 5, True, pc
        else:
            return 3, False, pc

    def __str__(self):
        return 'call p, nn'


class OpCallM(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        address, pc = fetch_word(memory, pc)
        if self.processor.condition('s'):
            call_to(self.processor, 3, address)
            return 5, True, pc
        else:
            return 3, False, pc

    def __str__(self):
        return 'call m, nn'


class OpRet(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        self.processor.restore_pc_from_stack()
        return 10, True, pc

    def __str__(self):
        return 'ret'


class OpRetNz(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        if not self.processor.condition('z'):
            self.processor.restore_pc_from_stack()
            return 11, True, pc
        else:
            return 5, False, pc

    def __str__(self):
        return 'ret nz'


class OpRetZ(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        if self.processor.condition('z'):
            self.processor.restore_pc_from_stack()
            return 11, True, pc
        else:
            return 5, False, pc

    def __str__(self):
        return 'ret z'


class OpRetNc(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        if not self.processor.condition('c'):
            self.processor.restore_pc_from_stack()
            return 11, True, pc
        else:
            return 5, False, pc

    def __str__(self):
        return 'ret nc'


class OpRetC(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        if self.processor.condition('c'):
            self.processor.restore_pc_from_stack()
            return 11, True, pc
        else:
            return 5, False, pc

    def __str__(self):
        return 'ret c'


class OpRetPo(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        if not self.processor.condition('p'):
            self.processor.restore_pc_from_stack()
            return 11, True, pc
        else:
            return 5, False, pc

    def __str__(self):
        return 'ret po'


class OpRetPe(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        if self.processor.condition('p'):
            self.processor.restore_pc_from_stack()
            return 11, True, pc
        else:
            return 5, False, pc

    def __str__(self):
        return 'ret pe'


class OpRetP(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        if not self.processor.condition('s'):
            self.processor.restore_pc_from_stack()
            return 11, True, pc
        else:
            return 5, False, pc

    def __str__(self):
        return 'ret p'


class OpRetM(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        if self.processor.condition('s'):
            self.processor.restore_pc_from_stack()
            return 11, True, pc
        else:
            return 5, False, pc

    def __str__(self):
        return 'ret m'


def call_to(processor, instruction_size, destination):
    sp_high, sp_low = high_low_pair(processor.special_registers['pc'] + instruction_size)
    processor.push_byte(sp_high)
    processor.push_byte(sp_low)
    processor.special_registers['pc'] = destination
