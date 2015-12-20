from baseop import BaseOp


class OpDi(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        self.processor.iff[0] = False
        self.processor.iff[1] = False

    def t_states(self):
        pass

    def __str__(self):
        return 'di'


class OpEi(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        self.processor.enable_iff = True

    def t_states(self):
        pass

    def __str__(self):
        return 'ei'


class OpRetn(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        self.processor.iff[0] = self.processor.iff[1]
        self.processor.restore_pc_from_stack()

    def t_states(self):
        pass

    def __str__(self):
        return 'retn'


class OpReti(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        self.processor.restore_pc_from_stack()

    def t_states(self):
        pass

    def __str__(self):
        return 'reti'


class OpHalt(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        self.processor.halting = True

    def t_states(self):
        pass

    def __str__(self):
        return 'halt'


class OpIm(BaseOp):
    def __init__(self, processor, interrupt_mode):
        BaseOp.__init__(self)
        self.processor = processor
        self.interrupt_mode = interrupt_mode

    def execute(self):
        self.processor.set_interrupt_mode(self.interrupt_mode)

    def t_states(self):
        pass

    def __str__(self):
        return 'im {}'.format(self.interrupt_mode)