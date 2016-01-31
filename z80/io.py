from z80.baseop import BaseOp
from z80.funcs import has_parity


class IO:
    def read(self, port, high_byte):
        raise NotImplementedError("Not implemented")

    def write(self, port, high_byte, value):
        raise NotImplementedError("Not implemented")


class OpInA(BaseOp):
    def __init__(self, processor, io):
        BaseOp.__init__(self)
        self.processor = processor
        self.io = io

    def execute(self):
        port = self.processor.get_next_byte()
        value = self.io.read(port, self.processor.main_registers['a'])
        self.processor.main_registers['a'] = value
        return 11

    def __str__(self):
        return 'in a, (n)'


class OpIn8RegC(BaseOp):
    def __init__(self, processor, io, dest_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.io = io
        self.dest_reg = dest_reg

    def execute(self):
        value = self.io.read(self.processor.main_registers['c'], self.processor.main_registers['b'])
        self.processor.main_registers[self.dest_reg] = value

        self.processor.set_condition('s', (value & 0b10000000) > 0)
        self.processor.set_condition('z', value == 0)
        self.processor.set_condition('h', False)
        self.processor.set_condition('p', has_parity(value))
        self.processor.set_condition('n', False)
        return 12

    def __str__(self):
        return 'in {}, (c)'.format(self.dest_reg)


class OpIni(BaseOp):
    def __init__(self, processor, memory, io):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.io = io

    def execute(self):
        _read_and_decrement_b(self.processor, self.memory, self.io, 1)
        self.processor.set_condition('z', self.processor.main_registers['b'] == 0)
        self.processor.set_condition('n', True)
        return 16

    def __str__(self):
        return 'ini'


class OpInir(BaseOp):
    def __init__(self, processor, memory, io):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.io = io
        self.last_t_states = None

    def execute(self):
        _read_and_decrement_b(self.processor, self.memory, self.io, 1)
        self.processor.set_condition('z', True)
        self.processor.set_condition('n', True)
        if self.processor.main_registers['b'] == 0:
            return 16
        else:
            self.processor.special_registers['pc'] = (self.processor.special_registers['pc'] - 2) & 0xffff
            return 21

    def __str__(self):
        return 'inir'


class OpInd(BaseOp):
    def __init__(self, processor, memory, io):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.io = io

    def execute(self):
        _read_and_decrement_b(self.processor, self.memory, self.io, -1)
        self.processor.set_condition('z', self.processor.main_registers['b'] == 0)
        self.processor.set_condition('n', True)
        return 16

    def __str__(self):
        return 'ind'


class OpIndr(BaseOp):
    def __init__(self, processor, memory, io):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.io = io
        self.last_t_states = None

    def execute(self):
        _read_and_decrement_b(self.processor, self.memory, self.io, -1)
        self.processor.set_condition('z', True)
        self.processor.set_condition('n', True)
        if self.processor.main_registers['b'] == 0:
            return 16
        else:
            self.processor.special_registers['pc'] = (self.processor.special_registers['pc'] - 2) & 0xffff
            return 21

    def __str__(self):
        return 'indr'


def _read_and_decrement_b(processor, memory, io, hl_increment):
    byte_counter = processor.main_registers['b']
    value = io.read(processor.main_registers['c'], byte_counter)
    destination = processor.get_16bit_reg('hl')
    memory[0xffff & destination] = value
    processor.main_registers['b'] = (byte_counter - 1) & 0xff
    processor.set_16bit_reg('hl', (destination + hl_increment) & 0xffff)


class OpOutA(BaseOp):
    def __init__(self, processor, io):
        BaseOp.__init__(self)
        self.processor = processor
        self.io = io

    def execute(self):
        port = self.processor.get_next_byte()
        self.io.write(port, self.processor.main_registers['a'], self.processor.main_registers['a'])
        return 11

    def __str__(self):
        return 'out (n), a'


class OpOutC8Reg(BaseOp):
    def __init__(self, processor, io, dest_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.io = io
        self.dest_reg = dest_reg

    def execute(self):
        self.io.write(self.processor.main_registers['c'], self.processor.main_registers['b'],
                      self.processor.main_registers[self.dest_reg])
        return 12

    def __str__(self):
        return 'out (c), {}'.format(self.dest_reg)


class OpOutCZero(BaseOp):
    def __init__(self, processor, io):
        BaseOp.__init__(self)
        self.processor = processor
        self.io = io

    def execute(self):
        self.io.write(self.processor.main_registers['c'], self.processor.main_registers['b'], 0)
        return 12

    def __str__(self):
        return 'out (c), 0'


class OpOuti(BaseOp):
    def __init__(self, processor, memory, io):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.io = io

    def execute(self):
        _write_and_decrement_b(self.processor, self.memory, self.io, 1)
        self.processor.set_condition('z', self.processor.main_registers['b'] == 0)
        self.processor.set_condition('n', True)
        return 16

    def __str__(self):
        return 'outi'


class OpOtir(BaseOp):
    def __init__(self, processor, memory, io):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.io = io
        self.last_t_states = None

    def execute(self):
        _write_and_decrement_b(self.processor, self.memory, self.io, 1)
        self.processor.set_condition('z', True)
        self.processor.set_condition('n', True)
        if self.processor.main_registers['b'] == 0:
            return 16
        else:
            self.processor.special_registers['pc'] = (self.processor.special_registers['pc'] - 2) & 0xffff
            return 21

    def __str__(self):
        return 'otir'


class OpOutd(BaseOp):
    def __init__(self, processor, memory, io):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.io = io

    def execute(self):
        _write_and_decrement_b(self.processor, self.memory, self.io, -1)
        self.processor.set_condition('z', self.processor.main_registers['b'] == 0)
        self.processor.set_condition('n', True)
        return 16

    def __str__(self):
        return 'outd'


class OpOtdr(BaseOp):
    def __init__(self, processor, memory, io):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.io = io
        self.last_t_states = None

    def execute(self):
        _write_and_decrement_b(self.processor, self.memory, self.io, -1)
        self.processor.set_condition('z', True)
        self.processor.set_condition('n', True)
        if self.processor.main_registers['b'] == 0:
            return 16
        else:
            self.processor.special_registers['pc'] = (self.processor.special_registers['pc'] - 2) & 0xffff
            return 21

    def __str__(self):
        return 'otdr'


def _write_and_decrement_b(processor, memory, io, hl_increment):
    processor.main_registers['b'] = (processor.main_registers['b'] - 1) & 0xff
    source = processor.get_16bit_reg('hl')
    io.write(processor.main_registers['c'], processor.main_registers['b'], memory[0xffff & source])
    processor.set_16bit_reg('hl', (source + hl_increment) & 0xffff)
