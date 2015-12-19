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


def _ex_with_alternate(processor, register_pair):
    old_main = [processor.main_registers[register_pair[0]], processor.main_registers[register_pair[1]]]
    processor.main_registers[register_pair[0]] = processor.alternate_registers[register_pair[0]]
    processor.main_registers[register_pair[1]] = processor.alternate_registers[register_pair[1]]
    processor.alternate_registers[register_pair[0]] = old_main[0]
    processor.alternate_registers[register_pair[1]] = old_main[1]
