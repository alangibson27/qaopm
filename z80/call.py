from funcs import big_endian_value, high_low_pair
from z80.baseop import BaseOp, CondOp


class OpCall(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        call_to(self.processor, _get_destination_from_pc(self.processor))

    def t_states(self):
        return 17

    def __str__(self):
        return 'call nn'


class OpCallDirect(BaseOp):
    def __init__(self, processor, address):
        BaseOp.__init__(self)
        self.processor = processor
        self.address = address

    def execute(self):
        call_to(self.processor, self.address)

    def t_states(self):
        return 17

    def __str__(self):
        return 'im2 response'


class OpRst(BaseOp):
    def __init__(self, processor, jump_address):
        BaseOp.__init__(self)
        self.processor = processor
        self.jump_address = jump_address

    def execute(self):
        call_to(self.processor, self.jump_address)

    def t_states(self):
        return 11

    def __str__(self):
        return 'rst {}'.format(hex(self.jump_address))


class OpCallNz(CondOp):
    def __init__(self, processor):
        CondOp.__init__(self)
        self.processor = processor

    def execute(self):
        address = _get_destination_from_pc(self.processor)
        if not self.processor.condition('z'):
            self.last_t_states = 5
            call_to(self.processor, address)
        else:
            self.last_t_states = 3

    def __str__(self):
        return 'call nz, nn'


class OpCallZ(CondOp):
    def __init__(self, processor):
        CondOp.__init__(self)
        self.processor = processor

    def execute(self):
        address = _get_destination_from_pc(self.processor)
        if self.processor.condition('z'):
            self.last_t_states = 5
            call_to(self.processor, address)
        else:
            self.last_t_states = 3

    def __str__(self):
        return 'call z, nn'


class OpCallNc(CondOp):
    def __init__(self, processor):
        CondOp.__init__(self)
        self.processor = processor

    def execute(self):
        address = _get_destination_from_pc(self.processor)
        if not self.processor.condition('c'):
            self.last_t_states = 5
            call_to(self.processor, address)
        else:
            self.last_t_states = 3

    def __str__(self):
        return 'call nc, nn'


class OpCallC(CondOp):
    def __init__(self, processor):
        CondOp.__init__(self)
        self.processor = processor

    def execute(self):
        address = _get_destination_from_pc(self.processor)
        if self.processor.condition('c'):
            self.last_t_states = 5
            call_to(self.processor, address)
        else:
            self.last_t_states = 3

    def __str__(self):
        return 'call c, nn'


class OpCallPo(CondOp):
    def __init__(self, processor):
        CondOp.__init__(self)
        self.processor = processor

    def execute(self):
        address = _get_destination_from_pc(self.processor)
        if not self.processor.condition('p'):
            self.last_t_states = 5
            call_to(self.processor, address)
        else:
            self.last_t_states = 3

    def __str__(self):
        return 'call po, nn'


class OpCallPe(CondOp):
    def __init__(self, processor):
        CondOp.__init__(self)
        self.processor = processor

    def execute(self):
        address = _get_destination_from_pc(self.processor)
        if self.processor.condition('p'):
            self.last_t_states = 5
            call_to(self.processor, address)
        else:
            self.last_t_states = 3

    def __str__(self):
        return 'call pe, nn'


class OpCallP(CondOp):
    def __init__(self, processor):
        CondOp.__init__(self)
        self.processor = processor

    def execute(self):
        address = _get_destination_from_pc(self.processor)
        if not self.processor.condition('s'):
            self.last_t_states = 5
            call_to(self.processor, address)
        else:
            self.last_t_states = 3

    def __str__(self):
        return 'call p, nn'


class OpCallM(CondOp):
    def __init__(self, processor):
        CondOp.__init__(self)
        self.processor = processor

    def execute(self):
        address = _get_destination_from_pc(self.processor)
        if self.processor.condition('s'):
            self.last_t_states = 5
            call_to(self.processor, address)
        else:
            self.last_t_states = 3

    def __str__(self):
        return 'call m, nn'


class OpRet(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        self.processor.restore_pc_from_stack()

    def t_states(self):
        return 10

    def __str__(self):
        return 'ret'


class OpRetNz(CondOp):
    def __init__(self, processor):
        CondOp.__init__(self)
        self.processor = processor

    def execute(self):
        if not self.processor.condition('z'):
            self.last_t_states = 11
            self.processor.restore_pc_from_stack()
        else:
            self.last_t_states = 5

    def __str__(self):
        return 'ret nz'


class OpRetZ(CondOp):
    def __init__(self, processor):
        CondOp.__init__(self)
        self.processor = processor

    def execute(self):
        if self.processor.condition('z'):
            self.last_t_states = 11
            self.processor.restore_pc_from_stack()
        else:
            self.last_t_states = 5

    def __str__(self):
        return 'ret z'


class OpRetNc(CondOp):
    def __init__(self, processor):
        CondOp.__init__(self)
        self.processor = processor

    def execute(self):
        if not self.processor.condition('c'):
            self.last_t_states = 11
            self.processor.restore_pc_from_stack()
        else:
            self.last_t_states = 5

    def __str__(self):
        return 'ret nc'


class OpRetC(CondOp):
    def __init__(self, processor):
        CondOp.__init__(self)
        self.processor = processor

    def execute(self):
        if self.processor.condition('c'):
            self.last_t_states = 11
            self.processor.restore_pc_from_stack()
        else:
            self.last_t_states = 5

    def __str__(self):
        return 'ret c'


class OpRetPo(CondOp):
    def __init__(self, processor):
        CondOp.__init__(self)
        self.processor = processor

    def execute(self):
        if not self.processor.condition('p'):
            self.last_t_states = 11
            self.processor.restore_pc_from_stack()
        else:
            self.last_t_states = 5

    def __str__(self):
        return 'ret po'


class OpRetPe(CondOp):
    def __init__(self, processor):
        CondOp.__init__(self)
        self.processor = processor

    def execute(self):
        if self.processor.condition('p'):
            self.last_t_states = 11
            self.processor.restore_pc_from_stack()
        else:
            self.last_t_states = 5

    def __str__(self):
        return 'ret pe'


class OpRetP(CondOp):
    def __init__(self, processor):
        CondOp.__init__(self)
        self.processor = processor

    def execute(self):
        if not self.processor.condition('s'):
            self.last_t_states = 11
            self.processor.restore_pc_from_stack()
        else:
            self.last_t_states = 5

    def __str__(self):
        return 'ret p'


class OpRetM(CondOp):
    def __init__(self, processor):
        CondOp.__init__(self)
        self.processor = processor

    def execute(self):
        if self.processor.condition('s'):
            self.last_t_states = 11
            self.processor.restore_pc_from_stack()
        else:
            self.last_t_states = 5

    def __str__(self):
        return 'ret m'


def call_to(processor, destination):
    sp_high, sp_low = high_low_pair(processor.special_registers['pc'])
    processor.push_byte(sp_high)
    processor.push_byte(sp_low)
    processor.special_registers['pc'] = destination


def _get_destination_from_pc(processor):
    next_pc_low = processor.get_next_byte()
    next_pc_high = processor.get_next_byte()
    return big_endian_value([next_pc_low, next_pc_high])
