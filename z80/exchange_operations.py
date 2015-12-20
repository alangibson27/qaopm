from baseop import BaseOp


class OpExAfAfPrime(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        _ex_with_alternate(self.processor, 'af')

    def t_states(self):
        pass

    def __str__(self):
        return "ex af, af'"


class OpExx(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        _ex_with_alternate(self.processor, 'bc')
        _ex_with_alternate(self.processor, 'de')
        _ex_with_alternate(self.processor, 'hl')

    def t_states(self):
        pass

    def __str__(self):
        return 'exx'


class OpExSpIndirectHl(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        old_h = self.processor.main_registers['h']
        old_l = self.processor.main_registers['l']

        self.processor.main_registers['h'] = self.memory.peek(self.processor.special_registers['sp'] + 1)
        self.processor.main_registers['l'] = self.memory.peek(self.processor.special_registers['sp'])

        self.memory.poke(self.processor.special_registers['sp'], old_l)
        self.memory.poke(self.processor.special_registers['sp'] + 1, old_h)

    def t_states(self):
        pass

    def __str__(self):
        return 'ex (sp), hl'


class OpExDeHl(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        old_h = self.processor.main_registers['h']
        old_l = self.processor.main_registers['l']
        self.processor.main_registers['h'] = self.processor.main_registers['d']
        self.processor.main_registers['l'] = self.processor.main_registers['e']
        self.processor.main_registers['d'] = old_h
        self.processor.main_registers['e'] = old_l

    def t_states(self):
        pass

    def __str__(self):
        return 'ex de, hl'


def _ex_with_alternate(processor, register_pair):
    old_main = [processor.main_registers[register_pair[0]], processor.main_registers[register_pair[1]]]
    processor.main_registers[register_pair[0]] = processor.alternate_registers[register_pair[0]]
    processor.main_registers[register_pair[1]] = processor.alternate_registers[register_pair[1]]
    processor.alternate_registers[register_pair[0]] = old_main[0]
    processor.alternate_registers[register_pair[1]] = old_main[1]
