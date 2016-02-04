from baseop import BaseOp


class OpLdAR(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        r_value = self.processor.special_registers['r']
        self.processor.main_registers['a'] = r_value
        self.processor.set_condition('s', r_value & 0b10000000 != 0)
        self.processor.set_condition('z', r_value == 0)
        self.processor.set_condition('h', False)
        self.processor.set_condition('p', self.processor.iff[1])
        self.processor.set_condition('n', False)
        return 9, False

    def __str__(self):
        return 'ld a, r'


class OpLdAI(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        self.processor.main_registers['a'] = self.processor.special_registers['i']
        return 9, False

    def __str__(self):
        return 'ld a, i'


class OpLdIA(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        self.processor.special_registers['i'] = self.processor.main_registers['a']
        return 9, False

    def __str__(self):
        return 'ld i, a'


class OpLdRA(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        self.processor.special_registers['r'] = self.processor.main_registers['a']
        return 9, False

    def __str__(self):
        return 'ld r, a'


class OpDi(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        self.processor.iff[0] = False
        self.processor.iff[1] = False
        return 4, False

    def __str__(self):
        return 'di'


class OpEi(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        self.processor.enable_iff = True
        return 4, False

    def __str__(self):
        return 'ei'


class OpRetn(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        self.processor.iff[0] = self.processor.iff[1]
        self.processor.restore_pc_from_stack()
        return 14, True

    def __str__(self):
        return 'retn'


class OpReti(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        self.processor.restore_pc_from_stack()
        return 14, True

    def __str__(self):
        return 'reti'


class OpHalt(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        self.processor.halting = True
        return 4, False

    def __str__(self):
        return 'halt'


class OpIm(BaseOp):
    def __init__(self, processor, interrupt_mode):
        BaseOp.__init__(self)
        self.processor = processor
        self.interrupt_mode = interrupt_mode

    def execute(self, instruction_bytes):
        self.processor.set_interrupt_mode(self.interrupt_mode)
        return 8, False

    def __str__(self):
        return 'im {}'.format(self.interrupt_mode)