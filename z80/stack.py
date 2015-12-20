from baseop import BaseOp


class OpPop16Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self):
        lsb = self.processor.pop_byte()
        msb = self.processor.pop_byte()
        self.processor.main_registers[self.reg[0]] = msb
        self.processor.main_registers[self.reg[1]] = lsb

    def t_states(self):
        pass

    def __str__(self):
        return 'pop {}'.format(self.reg)


class OpPush16Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self):
        self.processor.push_byte(self.processor.main_registers[self.reg[0]])
        self.processor.push_byte(self.processor.main_registers[self.reg[1]])

    def t_states(self):
        pass

    def __str__(self):
        return 'push {}'.format(self.reg)