from baseop import BaseOp
from z80.funcs import big_endian_value, high_low_pair


class OpExAfAfPrime(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        _ex_with_alternate(self.processor, 'af')
        return 4, False

    def __str__(self):
        return "ex af, af'"


class OpExx(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        _ex_with_alternate(self.processor, 'bc')
        _ex_with_alternate(self.processor, 'de')
        _ex_with_alternate(self.processor, 'hl')
        return 4, False

    def __str__(self):
        return 'exx'


class OpExSpIndirectHl(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self, instruction_bytes):
        old_h = self.processor.main_registers['h']
        old_l = self.processor.main_registers['l']

        self.processor.main_registers['h'] = self.memory[0xffff & (self.processor.special_registers['sp'] + 1)]
        self.processor.main_registers['l'] = self.memory[0xffff & self.processor.special_registers['sp']]

        self.memory[self.processor.special_registers['sp']] = old_l
        self.memory[0xffff & (self.processor.special_registers['sp'] + 1)] = old_h
        return 19, False

    def __str__(self):
        return 'ex (sp), hl'


class OpExDeHl(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, instruction_bytes):
        old_h = self.processor.main_registers['h']
        old_l = self.processor.main_registers['l']
        self.processor.main_registers['h'] = self.processor.main_registers['d']
        self.processor.main_registers['l'] = self.processor.main_registers['e']
        self.processor.main_registers['d'] = old_h
        self.processor.main_registers['e'] = old_l
        return 4, False

    def __str__(self):
        return 'ex de, hl'


class OpExSpIndirectIndexed(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self, instruction_bytes):
        old_index = self.processor.index_registers[self.indexed_reg]
        self.processor.index_registers[self.indexed_reg] = big_endian_value(
            [self.memory[self.processor.special_registers['sp']],
             self.memory[0xffff & (self.processor.special_registers['sp'] + 1)]])

        high_byte, low_byte = high_low_pair(old_index)
        self.memory[0xffff & self.processor.special_registers['sp']] = low_byte
        self.memory[0xffff & (self.processor.special_registers['sp'] + 1)] = high_byte
        return 23, False

    def __str__(self):
        return 'ex (sp), {}'.format(self.indexed_reg)


def _ex_with_alternate(processor, register_pair):
    old_main = [processor.main_registers[register_pair[0]], processor.main_registers[register_pair[1]]]
    processor.main_registers[register_pair[0]] = processor.alternate_registers[register_pair[0]]
    processor.main_registers[register_pair[1]] = processor.alternate_registers[register_pair[1]]
    processor.alternate_registers[register_pair[0]] = old_main[0]
    processor.alternate_registers[register_pair[1]] = old_main[1]
