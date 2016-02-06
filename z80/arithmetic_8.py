from memory.memory import fetch_byte, fetch_signed_byte
from z80.funcs import has_parity, to_signed, bitwise_add, bitwise_sub
from z80.baseop import BaseOp


class OpAddA8Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self, processor, memory, pc):
        _add_a(self.processor, self.processor.main_registers[self.reg], False)
        return 4, False, pc

    def __str__(self):
        return 'add a, {}'.format(self.reg)


class OpAdcA8Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self, processor, memory, pc):
        _add_a(self.processor, self.processor.main_registers[self.reg], self.processor.condition('c'))
        return 4, False, pc

    def __str__(self):
        return 'adc a, {}'.format(self.reg)


class OpAddAHlIndirect(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self, processor, memory, pc):
        value = self.memory[0xffff & self.processor.get_16bit_reg('hl')]
        _add_a(self.processor, value, False)
        return 7, False, pc

    def __str__(self):
        return 'add a, (hl)'


class OpAdcAHlIndirect(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self, processor, memory, pc):
        value = self.memory[0xffff & self.processor.get_16bit_reg('hl')]
        _add_a(self.processor, value, self.processor.condition('c'))
        return 7, False, pc

    def __str__(self):
        return 'adc a, (hl)'


class OpAddAImmediate(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self, processor, memory, pc):
        value, pc = fetch_byte(memory, pc)
        _add_a(self.processor, value, False)
        return 7, False, pc

    def __str__(self):
        return 'add a, n'


class OpAdcAImmediate(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self, processor, memory, pc):
        value, pc = fetch_byte(memory, pc)
        _add_a(self.processor, value, self.processor.condition('c'))
        return 7, False, pc

    def __str__(self):
        return 'adc a, n'


class OpSubA8Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self, processor, memory, pc):
        _sub_a(self.processor, self.processor.main_registers[self.reg], False)
        return 4, False, pc

    def __str__(self):
        return 'sub a, {}'.format(self.reg)


class OpSbcA8Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self, processor, memory, pc):
        _sub_a(self.processor, self.processor.main_registers[self.reg], self.processor.condition('c'))
        return 4, False, pc

    def __str__(self):
        return 'sbc a, {}'.format(self.reg)


class OpSubAHlIndirect(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self, processor, memory, pc):
        value = self.memory[0xffff & self.processor.get_16bit_reg('hl')]
        _sub_a(self.processor, value, False)
        return 7, False, pc

    def __str__(self):
        return 'sub a, (hl)'


class OpSbcAHlIndirect(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self, processor, memory, pc):
        value = self.memory[0xffff & self.processor.get_16bit_reg('hl')]
        _sub_a(self.processor, value, self.processor.condition('c'))
        return 7, False, pc

    def __str__(self):
        return 'sbc a, (hl)'


class OpSubAImmediate(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self, processor, memory, pc):
        value, pc = fetch_byte(memory, pc)
        _sub_a(self.processor, value, False)
        return 7, False, pc

    def __str__(self):
        return 'sub a, n'


class OpSbcAImmediate(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self, processor, memory, pc):
        value, pc = fetch_byte(memory, pc)
        _sub_a(self.processor, value, self.processor.condition('c'))
        return 7, False, pc

    def __str__(self):
        return 'sbc a, n'


class OpAddAIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self, processor, memory, pc):
        offset, pc = fetch_signed_byte(memory, pc)
        value = self.memory[0xffff & (self.processor.index_registers[self.indexed_reg] + offset)]
        _add_a(self.processor, value, False)
        return 19, False, pc

    def __str__(self):
        return 'add a, ({} + d)'.format(self.indexed_reg)


class OpAdcAIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self, processor, memory, pc):
        offset, pc = fetch_signed_byte(memory, pc)
        value = self.memory[0xffff & (self.processor.index_registers[self.indexed_reg] + offset)]
        _add_a(self.processor, value, self.processor.condition('c'))
        return 19, False, pc

    def __str__(self):
        return 'adc a, ({} + d)'.format(self.indexed_reg)


class OpSubAIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self, processor, memory, pc):
        offset, pc = fetch_signed_byte(memory, pc)
        value = self.memory[0xffff & (self.processor.index_registers[self.indexed_reg] + offset)]
        _sub_a(self.processor, value, False)
        return 19, False, pc

    def __str__(self):
        return 'sub a, ({} + d)'.format(self.indexed_reg)


class OpSbcAIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self, processor, memory, pc):
        offset, pc = fetch_signed_byte(memory, pc)
        value = self.memory[0xffff & (self.processor.index_registers[self.indexed_reg] + offset)]
        _sub_a(self.processor, value, self.processor.condition('c'))
        return 19, False, pc

    def __str__(self):
        return 'sbc a, ({} + d)'.format(self.indexed_reg)


class OpAndA8Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self, processor, memory, pc):
        _and_a_value(self.processor, self.processor.main_registers[self.reg])
        return 4, False, pc

    def __str__(self):
        return 'and {}'.format(self.reg)


class OpAndAHlIndirect(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self, processor, memory, pc):
        _and_a_value(self.processor, self.memory[0xffff & self.processor.get_16bit_reg('hl')])
        return 7, False, pc

    def __str__(self):
        return 'and (hl)'


class OpAndAImmediate(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        value, pc = fetch_byte(memory, pc)
        _and_a_value(self.processor, value)
        return 7, False, pc

    def __str__(self):
        return 'and a, n'


class OpAndIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self, processor, memory, pc):
        offset, pc = fetch_signed_byte(memory, pc)
        _and_a_value(self.processor, self.memory[0xffff & (self.processor.index_registers[self.indexed_reg] + offset)])
        return 19, False, pc

    def __str__(self):
        return 'and ({} + d)'.format(self.indexed_reg)


class OpXorA8Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self, processor, memory, pc):
        _xor_a_value(self.processor, self.processor.main_registers[self.reg])
        return 4, False, pc

    def __str__(self):
        return 'xor {}'.format(self.reg)


class OpXorAHlIndirect(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self, processor, memory, pc):
        _xor_a_value(self.processor, self.memory[0xffff & self.processor.get_16bit_reg('hl')])
        return 7, False, pc

    def __str__(self):
        return 'xor (hl)'


class OpXorAImmediate(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        value, pc = fetch_byte(memory, pc)
        _xor_a_value(self.processor, value)
        return 7, False, pc

    def __str__(self):
        return 'xor a, n'


class OpXorIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self, processor, memory, pc):
        offset, pc = fetch_signed_byte(memory, pc)
        _xor_a_value(self.processor, self.memory[0xffff & (self.processor.index_registers[self.indexed_reg] + offset)])
        return 19, False, pc

    def __str__(self):
        return 'xor ({} + d)'.format(self.indexed_reg)


class OpOrA8Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self, processor, memory, pc):
        _or_a_value(self.processor, self.processor.main_registers[self.reg])
        return 4, False, pc

    def __str__(self):
        return 'or {}'.format(self.reg)


class OpOrAHlIndirect(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self, processor, memory, pc):
        _or_a_value(self.processor, self.memory[0xffff & self.processor.get_16bit_reg('hl')])
        return 7, False, pc

    def __str__(self):
        return 'or (hl)'


class OpOrAImmediate(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        value, pc = fetch_byte(memory, pc)
        _or_a_value(self.processor, value)
        return 7, False, pc

    def __str__(self):
        return 'or a, n'


class OpOrIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self, processor, memory, pc):
        offset, pc = fetch_signed_byte(memory, pc)
        _or_a_value(self.processor, self.memory[0xffff & (self.processor.index_registers[self.indexed_reg] + offset)])
        return 19, False, pc

    def __str__(self):
        return 'or ({} + d)'.format(self.indexed_reg)


class OpCpA8Reg(BaseOp):
    def __init__(self, processor, reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.reg = reg

    def execute(self, processor, memory, pc):
        _cp_value(self.processor, self.processor.main_registers[self.reg], False)
        return 4, False, pc

    def __str__(self):
        return 'cp {}'.format(self.reg)


class OpCpAHlIndirect(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory

    def execute(self, processor, memory, pc):
        value = self.memory[0xffff & self.processor.get_16bit_reg('hl')]
        _cp_value(self.processor, value, False)
        return 7, False, pc

    def __str__(self):
        return 'cp (hl)'


class OpCpImmediate(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        value, pc = fetch_byte(memory, pc)
        _cp_value(self.processor, value, False)
        return 7, False, pc

    def __str__(self):
        return 'cp n'


class OpCpIndexedIndirect(BaseOp):
    def __init__(self, processor, memory, indexed_reg):
        BaseOp.__init__(self)
        self.processor = processor
        self.memory = memory
        self.indexed_reg = indexed_reg

    def execute(self, processor, memory, pc):
        offset, pc = fetch_signed_byte(memory, pc)
        _cp_value(self.processor, self.memory[0xffff & (self.processor.index_registers[self.indexed_reg] + offset)], False)
        return 19, False, pc

    def __str__(self):
        return 'cp ({} + d)'.format(self.indexed_reg)


class OpNeg(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        processor = self.processor
        result, half_carry, _ = bitwise_sub(0, processor.main_registers['a'])

        set_condition = processor.set_condition
        set_condition('s', to_signed(result) < 0)
        set_condition('z', result == 0)
        set_condition('h', half_carry)
        set_condition('p', processor.main_registers['a'] == 0x80)
        set_condition('n', True)
        set_condition('c', processor.main_registers['a'] != 0x00)
        processor.main_registers['a'] = result
        return 8, False, pc

    def __str__(self):
        return 'neg'


class OpCpl(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        processor = self.processor
        processor.main_registers['a'] = 0xff - processor.main_registers['a']
        processor.set_condition('h', True)
        processor.set_condition('n', True)
        return 4, False, pc

    def __str__(self):
        return 'cpl'


class OpScf(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        processor = self.processor
        processor.set_condition('h', False)
        processor.set_condition('n', False)
        processor.set_condition('c', True)
        return 4, False, pc

    def __str__(self):
        return 'scf'


class OpCcf(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        processor = self.processor
        processor.set_condition('h', processor.condition('c'))
        processor.set_condition('c', not processor.condition('c'))
        processor.set_condition('n', False)
        return 4, False, pc

    def __str__(self):
        return 'ccf'


class OpDaa(BaseOp):
    def __init__(self, processor):
        BaseOp.__init__(self)
        self.processor = processor

    def execute(self, processor, memory, pc):
        digits = [int(x,16) for x in hex(self.processor.main_registers['a'])[2:].zfill(2)]
        fc = self.processor.condition('c')
        hc = self.processor.condition('h')

        if self.processor.condition('n'):
            self._daa_after_sub(digits, fc, hc)
        else:
            self._daa_after_add(digits, fc, hc)
        return 4, False, pc

    def __str__(self):
        return 'daa'

    def _daa_after_add(self, digits, fc, hc):
        processor = self.processor
        if not fc and not hc:
            if digits[0] <= 0x9 and digits[1] <= 0x9:
                pass
            elif digits[0] <= 0x8 and digits[1] >= 0xa:
                processor.main_registers['a'] += 0x6
            elif digits[0] >= 0xa and digits[1] <= 0x9:
                processor.main_registers['a'] += 0x60
                processor.set_condition('c', True)
            elif digits[0] >= 0x9 and digits[1] >= 0xa:
                processor.main_registers['a'] += 0x66
                processor.set_condition('c', True)
        elif not fc and hc:
            if digits[0] <= 0x9 and digits[1] <= 0x3:
                processor.main_registers['a'] += 0x6
            elif digits[0] >= 0xa and digits[1] <= 0x3:
                processor.main_registers['a'] += 0x66
                processor.set_condition('c', True)
        elif fc and not hc:
            if digits[0] <= 0x2 and digits[1] <= 0x9:
                processor.main_registers['a'] += 0x60
                processor.set_condition('c', True)
            elif digits[0] <= 0x2 and digits[1] >= 0xa:
                processor.main_registers['a'] += 0x66
                processor.set_condition('c', True)
        elif fc and hc:
            if digits[0] <= 0x3 and digits[1] <= 0x3:
                processor.main_registers['a'] += 0x66
                processor.set_condition('c', True)

        processor.main_registers['a'] &= 0xff

        result = processor.main_registers['a']
        processor.set_condition('s', (result & 0b10000000) > 0)
        processor.set_condition('z', result == 0)
        processor.set_condition('p', has_parity(result))

    def _daa_after_sub(self, digits, fc, hc):
        processor = self.processor
        if not fc and not hc:
            if digits[0] <= 0x9 and digits[1] <= 0x9:
                pass
        elif not fc and hc:
            if digits[0] <= 0x8 and digits[1] >= 0x6:
                processor.main_registers['a'] += 0xfa
        elif fc and not hc:
            if digits[0] >= 0x7 and digits[1] <= 0x9:
                processor.main_registers['a'] += 0xa0
                processor.set_condition('c', True)
        elif fc and hc:
            if digits[0] >= 0x6 and digits[1] >= 0x6:
                processor.main_registers['a'] += 0x9a
                processor.set_condition('c', True)

        processor.main_registers['a'] &= 0xff

        result = processor.main_registers['a']
        processor.set_condition('s', (result & 0b10000000) > 0)
        processor.set_condition('z', result == 0)
        processor.set_condition('p', has_parity(result))


def _add_a(processor, value, carry):
    signed_a = to_signed(processor.main_registers['a'])
    if carry:
        value = (value + 1) & 0xff
    result, half_carry, full_carry = bitwise_add(processor.main_registers['a'], value)
    signed_result = to_signed(result)
    processor.main_registers['a'] = result
    set_condition = processor.set_condition
    set_condition('s', signed_result < 0)
    set_condition('z', result == 0)
    set_condition('h', half_carry)
    set_condition('p', (signed_a < 0) != (signed_result < 0))
    set_condition('n', False)
    set_condition('c', full_carry)


def _sub_a(processor, value, carry):
    signed_a = to_signed(processor.main_registers['a'])
    if carry:
        value = (value + 1) & 0xff
    result, half_carry, full_carry = bitwise_sub(processor.main_registers['a'], value)
    signed_result = to_signed(result)
    processor.main_registers['a'] = result
    set_condition = processor.set_condition
    set_condition('s', signed_result < 0)
    set_condition('z', result == 0)
    set_condition('h', half_carry)
    set_condition('p', (signed_a < 0) != (signed_result < 0))
    set_condition('n', True)
    set_condition('c', full_carry)


def _and_a_value(processor, value):
    result = processor.main_registers['a'] & value
    processor.main_registers['a'] = result
    set_condition = processor.set_condition
    set_condition('s', result & 0b10000000 > 0)
    set_condition('z', result == 0)
    set_condition('h', True)
    set_condition('p', has_parity(result))
    set_condition('n', False)
    set_condition('c', False)


def _xor_a_value(processor, value):
    result = processor.main_registers['a'] ^ value
    processor.main_registers['a'] = result

    set_condition = processor.set_condition
    set_condition('s', result & 0b10000000 > 0)
    set_condition('z', result == 0)
    set_condition('h', False)
    set_condition('p', has_parity(result))
    set_condition('n', False)
    set_condition('c', False)


def _or_a_value(processor, value):
    result = processor.main_registers['a'] | value
    processor.main_registers['a'] = result

    set_condition = processor.set_condition
    set_condition('s', result & 0b10000000 > 0)
    set_condition('z', result == 0)
    set_condition('h', False)
    set_condition('p', has_parity(result))
    set_condition('n', False)
    set_condition('c', False)


def _cp_value(processor, value, carry):
    signed_a = to_signed(processor.main_registers['a'])
    if carry:
        value = (value + 1) & 0xff
    result, half_carry, full_carry = bitwise_sub(processor.main_registers['a'], value)
    signed_result = to_signed(result)

    set_condition = processor.set_condition
    set_condition('s', signed_result < 0)
    set_condition('z', result == 0)
    set_condition('h', half_carry)
    set_condition('p', (signed_a < 0) != (signed_result < 0))
    set_condition('n', True)
    set_condition('c', full_carry)

