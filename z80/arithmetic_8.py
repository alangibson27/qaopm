from z80.funcs import has_parity, to_signed, bitwise_add, bitwise_sub
from z80.baseop import BaseOp


class OpAddA8Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self):
        _add_a(self.processor, self.processor.main_registers[self.reg], False)

    def t_states(self):
        return 4

    def __str__(self):
        return 'add a, {}'.format(self.reg)


class OpAdcA8Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self):
        _add_a(self.processor, self.processor.main_registers[self.reg], self.processor.condition('c'))

    def t_states(self):
        return 4

    def __str__(self):
        return 'adc a, {}'.format(self.reg)


class OpAddAHlIndirect(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        value = self.memory.peek(self.processor.get_16bit_reg('hl'))
        _add_a(self.processor, value, False)

    def t_states(self):
        return 7

    def __str__(self):
        return 'add a, (hl)'


class OpAdcAHlIndirect(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        value = self.memory.peek(self.processor.get_16bit_reg('hl'))
        _add_a(self.processor, value, self.processor.condition('c'))

    def t_states(self):
        return 7

    def __str__(self):
        return 'adc a, (hl)'


class OpAddAImmediate(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        value = self.processor.get_next_byte()
        _add_a(self.processor, value, False)

    def t_states(self):
        return 7

    def __str__(self):
        return 'add a, n'


class OpAdcAImmediate(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        value = self.processor.get_next_byte()
        _add_a(self.processor, value, self.processor.condition('c'))

    def t_states(self):
        return 7

    def __str__(self):
        return 'adc a, n'


class OpSubA8Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self):
        _sub_a(self.processor, self.processor.main_registers[self.reg], False)

    def t_states(self):
        return 4

    def __str__(self):
        return 'sub a, {}'.format(self.reg)


class OpSbcA8Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self):
        _sub_a(self.processor, self.processor.main_registers[self.reg], self.processor.condition('c'))

    def t_states(self):
        return 4

    def __str__(self):
        return 'sbc a, {}'.format(self.reg)


class OpSubAHlIndirect(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        value = self.memory.peek(self.processor.get_16bit_reg('hl'))
        _sub_a(self.processor, value, False)

    def t_states(self):
        return 7

    def __str__(self):
        return 'sub a, (hl)'


class OpSbcAHlIndirect(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        value = self.memory.peek(self.processor.get_16bit_reg('hl'))
        _sub_a(self.processor, value, self.processor.condition('c'))

    def t_states(self):
        return 7

    def __str__(self):
        return 'sbc a, (hl)'


class OpSubAImmediate(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        value = self.processor.get_next_byte()
        _sub_a(self.processor, value, False)

    def t_states(self):
        return 7

    def __str__(self):
        return 'sub a, n'


class OpSbcAImmediate(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self):
        value = self.processor.get_next_byte()
        _sub_a(self.processor, value, self.processor.condition('c'))

    def t_states(self):
        return 7

    def __str__(self):
        return 'sbc a, n'


class OpAddAIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self):
        offset = to_signed(self.processor.get_next_byte())
        value = self.memory.peek(self.processor.index_registers[self.indexed_reg] + offset)
        _add_a(self.processor, value, False)

    def t_states(self):
        return 19

    def __str__(self):
        return 'add a, ({} + d)'.format(self.indexed_reg)


class OpAdcAIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self):
        offset = to_signed(self.processor.get_next_byte())
        value = self.memory.peek(self.processor.index_registers[self.indexed_reg] + offset)
        _add_a(self.processor, value, self.processor.condition('c'))

    def t_states(self):
        return 19

    def __str__(self):
        return 'adc a, ({} + d)'.format(self.indexed_reg)


class OpSubAIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self):
        offset = to_signed(self.processor.get_next_byte())
        value = self.memory.peek(self.processor.index_registers[self.indexed_reg] + offset)
        _sub_a(self.processor, value, False)

    def t_states(self):
        return 19

    def __str__(self):
        return 'sub a, ({} + d)'.format(self.indexed_reg)


class OpSbcAIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self):
        offset = to_signed(self.processor.get_next_byte())
        value = self.memory.peek(self.processor.index_registers[self.indexed_reg] + offset)
        _sub_a(self.processor, value, self.processor.condition('c'))

    def t_states(self):
        return 19

    def __str__(self):
        return 'sbc a, ({} + d)'.format(self.indexed_reg)


class OpAndA8Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def t_states(self):
        return 4

    def execute(self):
        _and_a_value(self.processor, self.processor.main_registers[self.reg])

    def __str__(self):
        return 'and {}'.format(self.reg)


class OpAndAHlIndirect(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def t_states(self):
        return 7

    def execute(self):
        _and_a_value(self.processor, self.memory.peek(self.processor.get_16bit_reg('hl')))

    def __str__(self):
        return 'and (hl)'


class OpAndAImmediate(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        _and_a_value(self.processor, self.processor.get_next_byte())

    def t_states(self):
        return 7

    def __str__(self):
        return 'and a, n'


class OpAndIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self):
        offset = to_signed(self.processor.get_next_byte())
        _and_a_value(self.processor, self.memory.peek(self.processor.index_registers[self.indexed_reg] + offset))

    def t_states(self):
        return 19

    def __str__(self):
        return 'and ({} + d)'.format(self.indexed_reg)


class OpXorA8Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def t_states(self):
        return 4

    def execute(self):
        _xor_a_value(self.processor, self.processor.main_registers[self.reg])

    def __str__(self):
        return 'xor {}'.format(self.reg)


class OpXorAHlIndirect(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def t_states(self):
        return 7

    def execute(self):
        _xor_a_value(self.processor, self.memory.peek(self.processor.get_16bit_reg('hl')))

    def __str__(self):
        return 'xor (hl)'


class OpXorAImmediate(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        _xor_a_value(self.processor, self.processor.get_next_byte())

    def t_states(self):
        return 7

    def __str__(self):
        return 'xor a, n'


class OpXorIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self):
        offset = to_signed(self.processor.get_next_byte())
        _xor_a_value(self.processor, self.memory.peek(self.processor.index_registers[self.indexed_reg] + offset))

    def t_states(self):
        return 19

    def __str__(self):
        return 'xor ({} + d)'.format(self.indexed_reg)


class OpOrA8Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def t_states(self):
        return 4

    def execute(self):
        _or_a_value(self.processor, self.processor.main_registers[self.reg])

    def __str__(self):
        return 'or {}'.format(self.reg)


class OpOrAHlIndirect(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def t_states(self):
        return 7

    def execute(self):
        _or_a_value(self.processor, self.memory.peek(self.processor.get_16bit_reg('hl')))

    def __str__(self):
        return 'or (hl)'


class OpOrAImmediate(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        _or_a_value(self.processor, self.processor.get_next_byte())

    def t_states(self):
        return 7

    def __str__(self):
        return 'or a, n'


class OpOrIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self):
        offset = to_signed(self.processor.get_next_byte())
        _or_a_value(self.processor, self.memory.peek(self.processor.index_registers[self.indexed_reg] + offset))

    def t_states(self):
        return 19

    def __str__(self):
        return 'or ({} + d)'.format(self.indexed_reg)


class OpCpA8Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def t_states(self):
        return 4

    def execute(self):
        _cp_value(self.processor, self.processor.main_registers[self.reg], False)

    def __str__(self):
        return 'cp {}'.format(self.reg)


class OpCpAHlIndirect(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def t_states(self):
        return 7

    def execute(self):
        value = self.memory.peek(self.processor.get_16bit_reg('hl'))
        _cp_value(self.processor, value, False)

    def __str__(self):
        return 'cp (hl)'


class OpCpImmediate(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        _cp_value(self.processor, self.processor.get_next_byte(), False)

    def t_states(self):
        return 7

    def __str__(self):
        return 'cp n'


class OpCpIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self):
        offset = to_signed(self.processor.get_next_byte())
        _cp_value(self.processor, self.memory.peek(self.processor.index_registers[self.indexed_reg] + offset), False)

    def t_states(self):
        return 19

    def __str__(self):
        return 'cp ({} + d)'.format(self.indexed_reg)


class OpNeg(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        result, half_carry, _ = bitwise_sub(0, self.processor.main_registers['a'])

        self.processor.set_condition('s', to_signed(result) < 0)
        self.processor.set_condition('z', result == 0)
        self.processor.set_condition('h', half_carry)
        self.processor.set_condition('p', self.processor.main_registers['a'] == 0x80)
        self.processor.set_condition('n', True)
        self.processor.set_condition('c', self.processor.main_registers['a'] != 0x00)
        self.processor.main_registers['a'] = result

    def t_states(self):
        return 8

    def __str__(self):
        return 'neg'


class OpCpl(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        self.processor.main_registers['a'] = 0xff - self.processor.main_registers['a']
        self.processor.set_condition('h', True)
        self.processor.set_condition('n', True)

    def t_states(self):
        return 4

    def __str__(self):
        return 'cpl'


class OpScf(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        self.processor.set_condition('h', False)
        self.processor.set_condition('n', False)
        self.processor.set_condition('c', True)

    def t_states(self):
        return 4

    def __str__(self):
        return 'scf'


class OpCcf(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        self.processor.set_condition('h', self.processor.condition('c'))
        self.processor.set_condition('c', not self.processor.condition('c'))
        self.processor.set_condition('n', False)

    def t_states(self):
        return 4

    def __str__(self):
        return 'ccf'


class OpDaa(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self):
        digits = [int(x,16) for x in hex(self.processor.main_registers['a'])[2:].zfill(2)]
        fc = self.processor.condition('c')
        hc = self.processor.condition('h')

        if self.processor.condition('n'):
            self._daa_after_sub(digits, fc, hc)
        else:
            self._daa_after_add(digits, fc, hc)

    def t_states(self):
        return 4

    def __str__(self):
        return 'daa'

    def _daa_after_add(self, digits, fc, hc):
        if not fc and not hc:
            if digits[0] <= 0x9 and digits[1] <= 0x9:
                pass
            elif digits[0] <= 0x8 and digits[1] >= 0xa:
                self.processor.main_registers['a'] += 0x6
            elif digits[0] >= 0xa and digits[1] <= 0x9:
                self.processor.main_registers['a'] += 0x60
                self.processor.set_condition('c', True)
            elif digits[0] >= 0x9 and digits[1] >= 0xa:
                self.processor.main_registers['a'] += 0x66
                self.processor.set_condition('c', True)
        elif not fc and hc:
            if digits[0] <= 0x9 and digits[1] <= 0x3:
                self.processor.main_registers['a'] += 0x6
            elif digits[0] >= 0xa and digits[1] <= 0x3:
                self.processor.main_registers['a'] += 0x66
                self.processor.set_condition('c', True)
        elif fc and not hc:
            if digits[0] <= 0x2 and digits[1] <= 0x9:
                self.processor.main_registers['a'] += 0x60
                self.processor.set_condition('c', True)
            elif digits[0] <= 0x2 and digits[1] >= 0xa:
                self.processor.main_registers['a'] += 0x66
                self.processor.set_condition('c', True)
        elif fc and hc:
            if digits[0] <= 0x3 and digits[1] <= 0x3:
                self.processor.main_registers['a'] += 0x66
                self.processor.set_condition('c', True)

        self.processor.main_registers['a'] &= 0xff

        result = self.processor.main_registers['a']
        self.processor.set_condition('s', (result & 0b10000000) > 0)
        self.processor.set_condition('z', result == 0)
        self.processor.set_condition('p', has_parity(result))

    def _daa_after_sub(self, digits, fc, hc):
        if not fc and not hc:
            if digits[0] <= 0x9 and digits[1] <= 0x9:
                pass
        elif not fc and hc:
            if digits[0] <= 0x8 and digits[1] >= 0x6:
                self.processor.main_registers['a'] += 0xfa
        elif fc and not hc:
            if digits[0] >= 0x7 and digits[1] <= 0x9:
                self.processor.main_registers['a'] += 0xa0
                self.processor.set_condition('c', True)
        elif fc and hc:
            if digits[0] >= 0x6 and digits[1] >= 0x6:
                self.processor.main_registers['a'] += 0x9a
                self.processor.set_condition('c', True)

        self.processor.main_registers['a'] &= 0xff

        result = self.processor.main_registers['a']
        self.processor.set_condition('s', (result & 0b10000000) > 0)
        self.processor.set_condition('z', result == 0)
        self.processor.set_condition('p', has_parity(result))


def _add_a(processor, value, carry):
    signed_a = to_signed(processor.main_registers['a'])
    if carry:
        value = (value + 1) & 0xff
    result, half_carry, full_carry = bitwise_add(processor.main_registers['a'], value)
    signed_result = to_signed(result)
    processor.main_registers['a'] = result
    processor.set_condition('s', signed_result < 0)
    processor.set_condition('z', result == 0)
    processor.set_condition('h', half_carry)
    processor.set_condition('p', (signed_a < 0) != (signed_result < 0))
    processor.set_condition('n', False)
    processor.set_condition('c', full_carry)


def _sub_a(processor, value, carry):
    signed_a = to_signed(processor.main_registers['a'])
    if carry:
        value = (value + 1) & 0xff
    result, half_carry, full_carry = bitwise_sub(processor.main_registers['a'], value)
    signed_result = to_signed(result)
    processor.main_registers['a'] = result
    processor.set_condition('s', signed_result < 0)
    processor.set_condition('z', result == 0)
    processor.set_condition('h', half_carry)
    processor.set_condition('p', (signed_a < 0) != (signed_result < 0))
    processor.set_condition('n', True)
    processor.set_condition('c', full_carry)


def _and_a_value(processor, value):
    result = processor.main_registers['a'] & value
    processor.main_registers['a'] = result
    processor.set_condition('s', result & 0b10000000 > 0)
    processor.set_condition('z', result == 0)
    processor.set_condition('h', True)
    processor.set_condition('p', has_parity(result))
    processor.set_condition('n', False)
    processor.set_condition('c', False)


def _xor_a_value(processor, value):
    result = processor.main_registers['a'] ^ value
    processor.main_registers['a'] = result
    processor.set_condition('s', result & 0b10000000 > 0)
    processor.set_condition('z', result == 0)
    processor.set_condition('h', False)
    processor.set_condition('p', has_parity(result))
    processor.set_condition('n', False)
    processor.set_condition('c', False)


def _or_a_value(processor, value):
    result = processor.main_registers['a'] | value
    processor.main_registers['a'] = result
    processor.set_condition('s', result & 0b10000000 > 0)
    processor.set_condition('z', result == 0)
    processor.set_condition('h', False)
    processor.set_condition('p', has_parity(result))
    processor.set_condition('n', False)
    processor.set_condition('c', False)


def _cp_value(processor, value, carry):
    signed_a = to_signed(processor.main_registers['a'])
    if carry:
        value = (value + 1) & 0xff
    result, half_carry, full_carry = bitwise_sub(processor.main_registers['a'], value)
    signed_result = to_signed(result)
    processor.set_condition('s', signed_result < 0)
    processor.set_condition('z', result == 0)
    processor.set_condition('h', half_carry)
    processor.set_condition('p', (signed_a < 0) != (signed_result < 0))
    processor.set_condition('n', True)
    processor.set_condition('c', full_carry)

