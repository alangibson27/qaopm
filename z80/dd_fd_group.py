from z80.arithmetic_16 import *
from z80.arithmetic_8 import *
from z80.baseop import Undocumented
from z80.exchange_operations import *
from z80.inc_operations import *
from z80.indexed_cb_group import *
from z80.jump import *
from z80.ld_operations import *
from z80.stack import *


class OpDdFdGroup(BaseOp):
    def __init__(self, register, processor, memory):
        BaseOp.__init__(self)
        self.last_t_states = None
        self.processor = processor

        self.ops = {
            0x09: OpAddIndexedReg(processor, register, 'bc'),

            0x19: OpAddIndexedReg(processor, register, 'de'),

            0x21: OpLdIndexedImmediate(processor, register),
            0x22: OpLdExtIndexed(processor, memory, register),
            0x23: OpIncIndexed(processor, register),
            0x24: Undocumented('inc ixh'),
            0x25: Undocumented('dec ixh'),
            0x26: Undocumented('ld ixh, n'),
            0x29: OpAddIndexedReg(processor, register, register),
            0x2a: OpLdIndexedExt(processor, memory, register),
            0x2b: OpDecIndexed(processor, register),
            0x2c: Undocumented('inc ixl'),
            0x2d: Undocumented('dec ixl'),
            0x2e: Undocumented('ld ixl, n'),

            0x34: OpIncIndexedIndirect(processor, memory, register),
            0x35: OpDecIndexedIndirect(processor, memory, register),
            0x36: OpLdIndexedIndirectImmediate(processor, memory, register),
            0x39: OpAddIndexedReg(processor, register, 'sp'),

            0x44: Undocumented('ld b, ixh'),
            0x45: Undocumented('ld b, ixl'),
            0x46: OpLd8RegIndexedIndirect(processor, memory, 'b', register),
            0x4c: Undocumented('ld c, ixh'),
            0x4d: Undocumented('ld c, ixl'),
            0x4e: OpLd8RegIndexedIndirect(processor, memory, 'c', register),

            0x54: Undocumented('ld d, ixh'),
            0x55: Undocumented('ld d, ixl'),
            0x56: OpLd8RegIndexedIndirect(processor, memory, 'd', register),
            0x5c: Undocumented('ld e, ixh'),
            0x5d: Undocumented('ld e, ixl'),
            0x5e: OpLd8RegIndexedIndirect(processor, memory, 'e', register),

            0x60: Undocumented('ld ixh, b'),
            0x61: Undocumented('ld ixh, c'),
            0x62: Undocumented('ld ixh, d'),
            0x63: Undocumented('ld ixh, e'),
            0x64: Undocumented('ld ixh, h'),
            0x65: Undocumented('ld ixh, l'),
            0x66: OpLd8RegIndexedIndirect(processor, memory, 'h', register),
            0x67: Undocumented('ld ixl, a'),
            0x68: Undocumented('ld ixl, b'),
            0x69: Undocumented('ld ixl, c'),
            0x6a: Undocumented('ld ixl, d'),
            0x6b: Undocumented('ld ixl, e'),
            0x6c: Undocumented('ld ixl, h'),
            0x6d: Undocumented('ld ixl, l'),
            0x6e: OpLd8RegIndexedIndirect(processor, memory, 'l', register),
            0x6f: Undocumented('ld ixl, a'),

            0x70: OpLdIndexedIndirect8Reg(processor, memory, register, 'b'),
            0x71: OpLdIndexedIndirect8Reg(processor, memory, register, 'c'),
            0x72: OpLdIndexedIndirect8Reg(processor, memory, register, 'd'),
            0x73: OpLdIndexedIndirect8Reg(processor, memory, register, 'e'),
            0x74: OpLdIndexedIndirect8Reg(processor, memory, register, 'h'),
            0x75: OpLdIndexedIndirect8Reg(processor, memory, register, 'l'),
            0x77: OpLdIndexedIndirect8Reg(processor, memory, register, 'a'),
            0x7c: Undocumented('ld a, ixh'),
            0x7d: Undocumented('ld a, ixl'),
            0x7e: OpLd8RegIndexedIndirect(processor, memory, 'a', register),

            0x84: Undocumented('add a, ixh'),
            0x85: Undocumented('add a, ixl'),
            0x86: OpAddAIndexedIndirect(processor, memory, register),
            0x8c: Undocumented('adc a, ixh'),
            0x8d: Undocumented('adc a, ixl'),
            0x8e: OpAdcAIndexedIndirect(processor, memory, register),

            0x94: Undocumented('sub ixh'),
            0x95: Undocumented('sub ixl'),
            0x96: OpSubAIndexedIndirect(processor, memory, register),
            0x9c: Undocumented('sbc a, ixh'),
            0x9d: Undocumented('sbc a, ixl'),
            0x9e: OpSbcAIndexedIndirect(processor, memory, register),

            0xa4: Undocumented('and ixh'),
            0xa5: Undocumented('and ixl'),
            0xa6: OpAndIndexedIndirect(processor, memory, register),
            0xac: Undocumented('xor a, ixh'),
            0xad: Undocumented('xor a, ixl'),
            0xae: OpXorIndexedIndirect(processor, memory, register),

            0xb4: Undocumented('or ixh'),
            0xb5: Undocumented('or ixl'),
            0xb6: OpOrIndexedIndirect(processor, memory, register),
            0xbc: Undocumented('cp ixh'),
            0xbd: Undocumented('cp ixl'),
            0xbe: OpCpIndexedIndirect(processor, memory, register),

            0xcb: OpIndexedCbGroup(register, processor, memory),

            0xe1: OpPopIndexed(processor, register),
            0xe3: OpExSpIndirectIndexed(processor, memory, register),
            0xe5: OpPushIndexed(processor, register),
            0xe9: OpJpIndexedIndirect(processor, register),

            0xf9: OpLdSpIndexed(processor, register),
        }

    def execute(self):
        op = self.ops[self.processor.get_next_byte()]
        return op.execute()

    def __str__(self):
        return 'DD FD GROUP'

