from funcs import big_endian_value, high_low_pair
from z80.baseop import BaseOp


class OpCall(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        call_to(self.processor, _get_destination_from_pc(self.processor))

    def t_states(self):
        pass

    def __str__(self):
        return 'call nn'


class OpRst(BaseOp):
    def __init__(self, processor, jump_address):
        BaseOp.__init__(self)
        self.processor = processor
        self.jump_address = jump_address

    def execute(self):
        call_to(self.processor, self.jump_address)

    def t_states(self):
        pass

    def __str__(self):
        return 'rst {}'.format(hex(self.jump_address))


class OpCallNz(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        address = _get_destination_from_pc(self.processor)
        if not self.processor.condition('z'):
            call_to(self.processor, address)

    def t_states(self):
        pass

    def __str__(self):
        return 'call nz, nn'


class OpCallZ(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        address = _get_destination_from_pc(self.processor)
        if self.processor.condition('z'):
            call_to(self.processor, address)

    def t_states(self):
        pass

    def __str__(self):
        return 'call z, nn'


class OpCallNc(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        address = _get_destination_from_pc(self.processor)
        if not self.processor.condition('c'):
            call_to(self.processor, address)

    def t_states(self):
        pass

    def __str__(self):
        return 'call nc, nn'


class OpCallC(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        address = _get_destination_from_pc(self.processor)
        if self.processor.condition('c'):
            call_to(self.processor, address)

    def t_states(self):
        pass

    def __str__(self):
        return 'call c, nn'


class OpCallPo(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        address = _get_destination_from_pc(self.processor)
        if not self.processor.condition('p'):
            call_to(self.processor, address)

    def t_states(self):
        pass

    def __str__(self):
        return 'call po, nn'


class OpCallPe(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        address = _get_destination_from_pc(self.processor)
        if self.processor.condition('p'):
            call_to(self.processor, address)

    def t_states(self):
        pass

    def __str__(self):
        return 'call pe, nn'


class OpCallP(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        address = _get_destination_from_pc(self.processor)
        if not self.processor.condition('s'):
            call_to(self.processor, address)

    def t_states(self):
        pass

    def __str__(self):
        return 'call p, nn'


class OpCallM(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        address = _get_destination_from_pc(self.processor)
        if self.processor.condition('s'):
            call_to(self.processor, address)

    def t_states(self):
        pass

    def __str__(self):
        return 'call m, nn'


class OpRet(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        self.processor.special_registers['pc'] = _get_destination_from_stack(self.processor)

    def t_states(self):
        pass

    def __str__(self):
        return 'ret'


class OpRetNz(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        if not self.processor.condition('z'):
            self.processor.special_registers['pc'] = _get_destination_from_stack(self.processor)

    def t_states(self):
        pass

    def __str__(self):
        return 'ret nz'


class OpRetZ(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        if self.processor.condition('z'):
            self.processor.special_registers['pc'] = _get_destination_from_stack(self.processor)

    def t_states(self):
        pass

    def __str__(self):
        return 'ret z'


class OpRetNc(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        if not self.processor.condition('c'):
            self.processor.special_registers['pc'] = _get_destination_from_stack(self.processor)

    def t_states(self):
        pass

    def __str__(self):
        return 'ret nc'


class OpRetC(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        if self.processor.condition('c'):
            self.processor.special_registers['pc'] = _get_destination_from_stack(self.processor)

    def t_states(self):
        pass

    def __str__(self):
        return 'ret c'


class OpRetPo(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        if not self.processor.condition('p'):
            self.processor.special_registers['pc'] = _get_destination_from_stack(self.processor)

    def t_states(self):
        pass

    def __str__(self):
        return 'ret po'


class OpRetPe(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        if self.processor.condition('p'):
            self.processor.special_registers['pc'] = _get_destination_from_stack(self.processor)

    def t_states(self):
        pass

    def __str__(self):
        return 'ret pe'


class OpRetP(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        if not self.processor.condition('s'):
            self.processor.special_registers['pc'] = _get_destination_from_stack(self.processor)

    def t_states(self):
        pass

    def __str__(self):
        return 'ret p'


class OpRetM(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        if self.processor.condition('s'):
            self.processor.special_registers['pc'] = _get_destination_from_stack(self.processor)

    def t_states(self):
        pass

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


def _get_destination_from_stack(processor):
    return big_endian_value([processor.pop_byte(), processor.pop_byte()])
