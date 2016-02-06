from z80.arithmetic_16 import *
from z80.arithmetic_8 import *
from z80.block_operations import *
from z80.interrupt_operations import *
from z80.io import *
from z80.ld_operations import *
from z80.rotate import *


class OpEdGroup(BaseOp):
    def __init__(self, processor, memory, io):
        BaseOp.__init__(self)
        self.last_t_states = None
        self.processor = processor

        op_neg = OpNeg(processor)
        op_im0 = OpIm(processor, 0)
        op_in_a_c = OpIn8RegC(processor, io, 'a')
        op_retn = OpRetn(processor)
        self.ops = {
            0x40: OpIn8RegC(processor, io, 'b'),
            0x41: OpOutC8Reg(processor, io, 'b'),
            0x42: OpSbcHl16Reg(processor, 'bc'),
            0x43: OpLdAddress16Reg(processor, memory, 'bc'),
            0x44: op_neg,
            0x45: op_retn,
            0x46: op_im0,
            0x47: OpLdIA(processor),
            0x48: OpIn8RegC(processor, io, 'c'),
            0x49: OpOutC8Reg(processor, io, 'c'),
            0x4a: OpAdcHl16Reg(processor, 'bc'),
            0x4b: OpLd16RegAddress(processor, memory, 'bc'),
            0x4c: op_neg,
            0x4d: OpReti(processor),
            0x4e: op_im0,
            0x4f: OpLdRA(processor),

            0x50: OpIn8RegC(processor, io, 'd'),
            0x51: OpOutC8Reg(processor, io, 'd'),
            0x52: OpSbcHl16Reg(processor, 'de'),
            0x53: OpLdAddress16Reg(processor, memory, 'de'),
            0x54: op_neg,
            0x55: op_retn,
            0x56: OpIm(processor, 1),
            0x57: OpLdAI(processor),
            0x58: OpIn8RegC(processor, io, 'e'),
            0x59: OpOutC8Reg(processor, io, 'e'),
            0x5a: OpAdcHl16Reg(processor, 'de'),
            0x5b: OpLd16RegAddress(processor, memory, 'de'),
            0x5c: op_neg,
            0x5d: op_retn,
            0x5e: OpIm(processor, 2),
            0x5f: OpLdAR(processor),

            0x60: OpIn8RegC(processor, io, 'h'),
            0x61: OpOutC8Reg(processor, io, 'h'),
            0x62: OpSbcHl16Reg(processor, 'hl'),
            0x63: OpLdAddress16Reg(processor, memory, 'hl'),
            0x64: op_neg,
            0x65: op_retn,
            0x66: OpIm(processor, 0),
            0x67: OpRrd(processor, memory),
            0x68: OpIn8RegC(processor, io, 'l'),
            0x69: OpOutC8Reg(processor, io, 'l'),
            0x6a: OpAdcHl16Reg(processor, 'hl'),
            0x6b: OpLd16RegAddress(processor, memory, 'hl'),
            0x6c: op_neg,
            0x6d: op_retn,
            0x6e: op_im0,
            0x6f: OpRld(processor, memory),

            0x70: op_in_a_c,
            0x71: OpOutCZero(processor, io),
            0x72: OpSbcHl16Reg(processor, 'sp'),
            0x73: OpLdExtSp(processor, memory),
            0x74: op_neg,
            0x75: op_retn,
            0x76: OpIm(processor, 1),
            0x78: op_in_a_c,
            0x79: OpOutC8Reg(processor, io, 'a'),
            0x7a: OpAdcHl16Reg(processor, 'sp'),
            0x7b: OpLdSpExt(processor, memory),
            0x7c: op_neg,
            0x7d: op_retn,
            0x7e: OpIm(processor, 2),

            0xa0: OpLdi(processor, memory),
            0xa1: OpCpi(processor, memory),
            0xa2: OpIni(processor, memory, io),
            0xa3: OpOuti(processor, memory, io),
            0xa8: OpLdd(processor, memory),
            0xa9: OpCpd(processor, memory),
            0xaa: OpInd(processor, memory, io),
            0xab: OpOutd(processor, memory, io),

            0xb0: OpLdir(processor, memory),
            0xb1: OpCpir(processor, memory),
            0xb2: OpInir(processor, memory, io),
            0xb3: OpOtir(processor, memory, io),
            0xb8: OpLddr(processor, memory),
            0xb9: OpCpdr(processor, memory),
            0xba: OpIndr(processor, memory, io),
            0xbb: OpOtdr(processor, memory, io)
        }

    def execute(self, processor, memory, pc):
        code, pc = fetch_byte(memory, pc)
        op = self.ops[code]
        return op.execute(processor, memory, pc)

    def __str__(self):
        return 'ED GROUP'

