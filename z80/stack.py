from baseop import BaseOp
from z80.funcs import big_endian_value, high_low_pair


class OpPop16Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self, processor, memory, pc):
        lsb = self.processor.pop_byte()
        msb = self.processor.pop_byte()
        self.processor.main_registers[self.reg[0]] = msb
        self.processor.main_registers[self.reg[1]] = lsb
        return 10, False, pc

    def __str__(self):
        return 'pop {}'.format(self.reg)


class OpPopIndexed(BaseOp):
    def __init__(self, processor, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.indexed_reg = indexed_reg

    def execute(self, processor, memory, pc):
        lsb = self.processor.pop_byte()
        msb = self.processor.pop_byte()
        self.processor.index_registers[self.indexed_reg] = big_endian_value([lsb, msb])
        return 14, False, pc

    def __str__(self):
        return 'pop {}'.format(self.indexed_reg)


class OpPush16Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self, processor, memory, pc):
        self.processor.push_byte(self.processor.main_registers[self.reg[0]])
        self.processor.push_byte(self.processor.main_registers[self.reg[1]])
        return 11, False, pc

    def __str__(self):
        return 'push {}'.format(self.reg)


class OpPushIndexed(BaseOp):
    def __init__(self, processor, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.indexed_reg = indexed_reg

    def execute(self, processor, memory, pc):
        high_byte, low_byte = high_low_pair(self.processor.index_registers[self.indexed_reg])
        self.processor.push_byte(high_byte)
        self.processor.push_byte(low_byte)
        return 15, False, pc

    def __str__(self):
        return 'pop {}'.format(self.indexed_reg)
