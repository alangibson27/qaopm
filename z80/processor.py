from arithmetic_16 import *
from baseop import *
from bit import *
from call import *
from exchange_operations import *
from inc_operations import *
from interrupt_operations import *
from jump import *
from ld_operations import *
from rotate import *
from shift import *
from stack import *
from z80.arithmetic_8 import *
from z80.block_operations import *
from z80.io import *


class Op:
    def __init__(self, function, mnemonic):
        self.function = function
        self.mnemonic = mnemonic


class Processor:
    def __init__(self, memory, io):
        self.memory = memory
        self.io = io
        self.main_registers = self.build_swappable_register_set()
        self.alternate_registers = self.build_swappable_register_set()
        self.special_registers = self.build_special_register_set()
        self.index_registers = self.build_index_register_set()
        self.operations_by_opcode = self.init_opcode_map()
        self.enable_iff = False
        self.iff = [False, False]
        self.interrupt_data_queue = []
        self.interrupt_mode = 0
        self.interrupt_requests = []
        self.halting = False
        self.im1_response_op = OpRst(self, 0x0038)
        self.condition_masks = {
            'c': 0b00000001,
            'n': 0b00000010,
            'p': 0b00000100,
            'h': 0b00010000,
            'z': 0b01000000,
            's': 0b10000000
        }

    @staticmethod
    def build_swappable_register_set():
        return {'a': 0x0, 'f': 0x0, 'b': 0x0, 'c': 0x0, 'd': 0x0, 'e': 0x0, 'h': 0x0, 'l': 0x0}

    @staticmethod
    def build_index_register_set():
        return {'ix': 0x0000, 'iy': 0x0000}

    @staticmethod
    def build_special_register_set():
        return {'i': 0x0, 'r': 0x0, 'sp': 0xffff, 'pc': 0x0000}

    def init_opcode_map(self):
        return {
            0x00: Nop(),

            0x01: OpLd16RegImmediate(self, self.memory, 'bc'),
            0x02: OpLd16RegIndirectFrom8Reg(self, self.memory, 'bc', 'a'),
            0x03: OpInc16Reg(self, 'bc'),
            0x04: OpInc8Reg(self, 'b'),
            0x05: OpDec8Reg(self, 'b'),
            0x06: OpLd8RegImmediate(self, 'b'),
            0x07: OpRlca(self),
            0x08: OpExAfAfPrime(self),
            0x09: OpAddHl16Reg(self, 'bc'),
            0x0a: OpLd8RegFrom16RegIndirect(self, self.memory, 'a', 'bc'),
            0x0b: OpDec16Reg(self, 'bc'),
            0x0c: OpInc8Reg(self, 'c'),
            0x0d: OpDec8Reg(self, 'c'),
            0x0e: OpLd8RegImmediate(self, 'c'),
            0x0f: OpRrca(self),

            0x10: OpDjnz(self),
            0x11: OpLd16RegImmediate(self, self.memory, 'de'),
            0x12: OpLd16RegIndirectFrom8Reg(self, self.memory, 'de', 'a'),
            0x13: OpInc16Reg(self, 'de'),
            0x14: OpInc8Reg(self, 'd'),
            0x15: OpDec8Reg(self, 'd'),
            0x16: OpLd8RegImmediate(self, 'd'),
            0x17: OpRla(self),
            0x18: OpJr(self),
            0x19: OpAddHl16Reg(self, 'de'),
            0x1a: OpLd8RegFrom16RegIndirect(self, self.memory, 'a', 'de'),
            0x1b: OpDec16Reg(self, 'de'),
            0x1c: OpInc8Reg(self, 'e'),
            0x1d: OpDec8Reg(self, 'e'),
            0x1e: OpLd8RegImmediate(self, 'e'),
            0x1f: OpRra(self),

            0x20: OpJrNz(self),
            0x21: OpLd16RegImmediate(self, self.memory, 'hl'),
            0x22: OpLdAddressHl(self, self.memory),
            0x23: OpInc16Reg(self, 'hl'),
            0x24: OpInc8Reg(self, 'h'),
            0x25: OpDec8Reg(self, 'h'),
            0x26: OpLd8RegImmediate(self, 'h'),
            0x27: OpDaa(self),
            0x28: OpJrZ(self),
            0x29: OpAddHl16Reg(self, 'hl'),
            0x2a: OpLdHlAddress(self, self.memory),
            0x2b: OpDec16Reg(self, 'hl'),
            0x2c: OpInc8Reg(self, 'l'),
            0x2d: OpDec8Reg(self, 'l'),
            0x2e: OpLd8RegImmediate(self, 'l'),
            0x2f: OpCpl(self),

            0x30: OpJrNc(self),
            0x31: OpLdSpImmediate(self),
            0x32: OpLdAddressA(self, self.memory),
            0x33: OpInc16Reg(self, 'sp'),
            0x34: OpIncHlIndirect(self, self.memory),
            0x35: OpDecHlIndirect(self, self.memory),
            0x36: OpLdHlIndirectImmediate(self, self.memory),
            0x37: OpScf(self),
            0x38: OpJrC(self),
            0x39: OpAddHl16Reg(self, 'sp'),
            0x3a: OpLdAAddress(self, self.memory),
            0x3b: OpDec16Reg(self, 'sp'),
            0x3c: OpInc8Reg(self, 'a'),
            0x3d: OpDec8Reg(self, 'a'),
            0x3e: OpLd8RegImmediate(self, 'a'),
            0x3f: OpCcf(self),

            0x40: OpLd8RegFrom8Reg(self, 'b', 'b'),
            0x41: OpLd8RegFrom8Reg(self, 'b', 'c'),
            0x42: OpLd8RegFrom8Reg(self, 'b', 'd'),
            0x43: OpLd8RegFrom8Reg(self, 'b', 'e'),
            0x44: OpLd8RegFrom8Reg(self, 'b', 'h'),
            0x45: OpLd8RegFrom8Reg(self, 'b', 'l'),
            0x46: OpLd8RegFrom16RegIndirect(self, self.memory, 'b', 'hl'),
            0x47: OpLd8RegFrom8Reg(self, 'b', 'a'),
            0x48: OpLd8RegFrom8Reg(self, 'c', 'b'),
            0x49: OpLd8RegFrom8Reg(self, 'c', 'c'),
            0x4a: OpLd8RegFrom8Reg(self, 'c', 'd'),
            0x4b: OpLd8RegFrom8Reg(self, 'c', 'e'),
            0x4c: OpLd8RegFrom8Reg(self, 'c', 'h'),
            0x4d: OpLd8RegFrom8Reg(self, 'c', 'l'),
            0x4e: OpLd8RegFrom16RegIndirect(self, self.memory, 'c', 'hl'),
            0x4f: OpLd8RegFrom8Reg(self, 'c', 'a'),

            0x50: OpLd8RegFrom8Reg(self, 'd', 'b'),
            0x51: OpLd8RegFrom8Reg(self, 'd', 'c'),
            0x52: OpLd8RegFrom8Reg(self, 'd', 'd'),
            0x53: OpLd8RegFrom8Reg(self, 'd', 'e'),
            0x54: OpLd8RegFrom8Reg(self, 'd', 'h'),
            0x55: OpLd8RegFrom8Reg(self, 'd', 'l'),
            0x56: OpLd8RegFrom16RegIndirect(self, self.memory, 'd', 'hl'),
            0x57: OpLd8RegFrom8Reg(self, 'd', 'a'),
            0x58: OpLd8RegFrom8Reg(self, 'e', 'b'),
            0x59: OpLd8RegFrom8Reg(self, 'e', 'c'),
            0x5a: OpLd8RegFrom8Reg(self, 'e', 'd'),
            0x5b: OpLd8RegFrom8Reg(self, 'e', 'e'),
            0x5c: OpLd8RegFrom8Reg(self, 'e', 'h'),
            0x5d: OpLd8RegFrom8Reg(self, 'e', 'l'),
            0x5e: OpLd8RegFrom16RegIndirect(self, self.memory, 'e', 'hl'),
            0x5f: OpLd8RegFrom8Reg(self, 'e', 'a'),

            0x60: OpLd8RegFrom8Reg(self, 'h', 'b'),
            0x61: OpLd8RegFrom8Reg(self, 'h', 'c'),
            0x62: OpLd8RegFrom8Reg(self, 'h', 'd'),
            0x63: OpLd8RegFrom8Reg(self, 'h', 'e'),
            0x64: OpLd8RegFrom8Reg(self, 'h', 'h'),
            0x65: OpLd8RegFrom8Reg(self, 'h', 'l'),
            0x66: OpLd8RegFrom16RegIndirect(self, self.memory, 'h', 'hl'),
            0x67: OpLd8RegFrom8Reg(self, 'h', 'a'),
            0x68: OpLd8RegFrom8Reg(self, 'l', 'b'),
            0x69: OpLd8RegFrom8Reg(self, 'l', 'c'),
            0x6a: OpLd8RegFrom8Reg(self, 'l', 'd'),
            0x6b: OpLd8RegFrom8Reg(self, 'l', 'e'),
            0x6c: OpLd8RegFrom8Reg(self, 'l', 'h'),
            0x6d: OpLd8RegFrom8Reg(self, 'l', 'l'),
            0x6e: OpLd8RegFrom16RegIndirect(self, self.memory, 'l', 'hl'),
            0x6f: OpLd8RegFrom8Reg(self, 'l', 'a'),

            0x70: OpLd16RegIndirectFrom8Reg(self, self.memory, 'hl', 'b'),
            0x71: OpLd16RegIndirectFrom8Reg(self, self.memory, 'hl', 'c'),
            0x72: OpLd16RegIndirectFrom8Reg(self, self.memory, 'hl', 'd'),
            0x73: OpLd16RegIndirectFrom8Reg(self, self.memory, 'hl', 'e'),
            0x74: OpLd16RegIndirectFrom8Reg(self, self.memory, 'hl', 'h'),
            0x75: OpLd16RegIndirectFrom8Reg(self, self.memory, 'hl', 'l'),
            0x76: OpHalt(self),
            0x77: OpLd16RegIndirectFrom8Reg(self, self.memory, 'hl', 'a'),
            0x78: OpLd8RegFrom8Reg(self, 'a', 'b'),
            0x79: OpLd8RegFrom8Reg(self, 'a', 'c'),
            0x7a: OpLd8RegFrom8Reg(self, 'a', 'd'),
            0x7b: OpLd8RegFrom8Reg(self, 'a', 'e'),
            0x7c: OpLd8RegFrom8Reg(self, 'a', 'h'),
            0x7d: OpLd8RegFrom8Reg(self, 'a', 'l'),
            0x7e: OpLd8RegFrom16RegIndirect(self, self.memory, 'a', 'hl'),
            0x7f: OpLd8RegFrom8Reg(self, 'a', 'a'),

            0x80: OpAddA8Reg(self, 'b'),
            0x81: OpAddA8Reg(self, 'c'),
            0x82: OpAddA8Reg(self, 'd'),
            0x83: OpAddA8Reg(self, 'e'),
            0x84: OpAddA8Reg(self, 'h'),
            0x85: OpAddA8Reg(self, 'l'),
            0x86: OpAddAHlIndirect(self, self.memory),
            0x87: OpAddA8Reg(self, 'a'),
            0x88: OpAdcA8Reg(self, 'b'),
            0x89: OpAdcA8Reg(self, 'c'),
            0x8a: OpAdcA8Reg(self, 'd'),
            0x8b: OpAdcA8Reg(self, 'e'),
            0x8c: OpAdcA8Reg(self, 'h'),
            0x8d: OpAdcA8Reg(self, 'l'),
            0x8e: OpAdcAHlIndirect(self, self.memory),
            0x8f: OpAdcA8Reg(self, 'a'),

            0x90: OpSubA8Reg(self, 'b'),
            0x91: OpSubA8Reg(self, 'c'),
            0x92: OpSubA8Reg(self, 'd'),
            0x93: OpSubA8Reg(self, 'e'),
            0x94: OpSubA8Reg(self, 'h'),
            0x95: OpSubA8Reg(self, 'l'),
            0x96: OpSubAHlIndirect(self, self.memory),
            0x97: OpSubA8Reg(self, 'a'),
            0x98: OpSbcA8Reg(self, 'b'),
            0x99: OpSbcA8Reg(self, 'c'),
            0x9a: OpSbcA8Reg(self, 'd'),
            0x9b: OpSbcA8Reg(self, 'e'),
            0x9c: OpSbcA8Reg(self, 'h'),
            0x9d: OpSbcA8Reg(self, 'l'),
            0x9e: OpSbcAHlIndirect(self, self.memory),
            0x9f: OpSbcA8Reg(self, 'a'),

            0xa0: OpAndA8Reg(self, 'b'),
            0xa1: OpAndA8Reg(self, 'c'),
            0xa2: OpAndA8Reg(self, 'd'),
            0xa3: OpAndA8Reg(self, 'e'),
            0xa4: OpAndA8Reg(self, 'h'),
            0xa5: OpAndA8Reg(self, 'l'),
            0xa6: OpAndAHlIndirect(self, self.memory),
            0xa7: OpAndA8Reg(self, 'a'),
            0xa8: OpXorA8Reg(self, 'b'),
            0xa9: OpXorA8Reg(self, 'c'),
            0xaa: OpXorA8Reg(self, 'd'),
            0xab: OpXorA8Reg(self, 'e'),
            0xac: OpXorA8Reg(self, 'h'),
            0xad: OpXorA8Reg(self, 'l'),
            0xae: OpXorAHlIndirect(self, self.memory),
            0xaf: OpXorA8Reg(self, 'a'),

            0xb0: OpOrA8Reg(self, 'b'),
            0xb1: OpOrA8Reg(self, 'c'),
            0xb2: OpOrA8Reg(self, 'd'),
            0xb3: OpOrA8Reg(self, 'e'),
            0xb4: OpOrA8Reg(self, 'h'),
            0xb5: OpOrA8Reg(self, 'l'),
            0xb6: OpOrAHlIndirect(self, self.memory),
            0xb7: OpOrA8Reg(self, 'a'),
            0xb8: OpCpA8Reg(self, 'b'),
            0xb9: OpCpA8Reg(self, 'c'),
            0xba: OpCpA8Reg(self, 'd'),
            0xbb: OpCpA8Reg(self, 'e'),
            0xbc: OpCpA8Reg(self, 'h'),
            0xbd: OpCpA8Reg(self, 'l'),
            0xbe: OpCpAHlIndirect(self, self.memory),
            0xbf: OpCpA8Reg(self, 'a'),

            0xc0: OpRetNz(self),
            0xc1: OpPop16Reg(self, 'bc'),
            0xc2: OpJpNz(self),
            0xc3: OpJp(self),
            0xc4: OpCallNz(self),
            0xc5: OpPush16Reg(self, 'bc'),
            0xc6: OpAddAImmediate(self, self.memory),
            0xc7: OpRst(self, 0x00),
            0xc8: OpRetZ(self),
            0xc9: OpRet(self),
            0xca: OpJpZ(self),
            0xcc: OpCallZ(self),
            0xcd: OpCall(self),
            0xce: OpAdcAImmediate(self, self.memory),
            0xcf: OpRst(self, 0x08),

            0xd0: OpRetNc(self),
            0xd1: OpPop16Reg(self, 'de'),
            0xd2: OpJpNc(self),
            0xd3: OpOutA(self, self.io),
            0xd4: OpCallNc(self),
            0xd5: OpPush16Reg(self, 'de'),
            0xd6: OpSubAImmediate(self, self.memory),
            0xd7: OpRst(self, 0x10),
            0xd8: OpRetC(self),
            0xd9: OpExx(self),
            0xda: OpJpC(self),
            0xdb: OpInA(self, self.io),
            0xdc: OpCallC(self),
            0xde: OpSbcAImmediate(self, self.memory),
            0xdf: OpRst(self, 0x18),

            0xe0: OpRetPo(self),
            0xe1: OpPop16Reg(self, 'hl'),
            0xe2: OpJpPo(self),
            0xe3: OpExSpIndirectHl(self, self.memory),
            0xe4: OpCallPo(self),
            0xe5: OpPush16Reg(self, 'hl'),
            0xe6: OpAndAImmediate(self),
            0xe7: OpRst(self, 0x20),
            0xe8: OpRetPe(self),
            0xe9: OpJpHlIndirect(self),
            0xea: OpJpPe(self),
            0xeb: OpExDeHl(self),
            0xec: OpCallPe(self),
            0xee: OpXorAImmediate(self),
            0xef: OpRst(self, 0x28),

            0xf0: OpRetP(self),
            0xf1: OpPop16Reg(self, 'af'),
            0xf2: OpJpP(self),
            0xf3: OpDi(self),
            0xf4: OpCallP(self),
            0xf5: OpPush16Reg(self, 'af'),
            0xf6: OpOrAImmediate(self),
            0xf7: OpRst(self, 0x30),
            0xf8: OpRetM(self),
            0xf9: OpLdSpHl(self),
            0xfa: OpJpM(self),
            0xfb: OpEi(self),
            0xfc: OpCallM(self),
            0xfe: OpCpImmediate(self),
            0xff: OpRst(self, 0x38),

            0xcb: self.init_cb_opcodes(),
            0xed: self.init_ed_opcodes(),
            0xdd: self.init_dd_opcodes(),
            0xfd: self.init_fd_opcodes()
        }

    def init_cb_opcodes(self):
        return {
            0x00: OpRlcReg(self, 'b'),
            0x01: OpRlcReg(self, 'c'),
            0x02: OpRlcReg(self, 'd'),
            0x03: OpRlcReg(self, 'e'),
            0x04: OpRlcReg(self, 'h'),
            0x05: OpRlcReg(self, 'l'),
            0x06: OpRlcHlIndirect(self, self.memory),
            0x07: OpRlcReg(self, 'a'),
            0x08: OpRrcReg(self, 'b'),
            0x09: OpRrcReg(self, 'c'),
            0x0a: OpRrcReg(self, 'd'),
            0x0b: OpRrcReg(self, 'e'),
            0x0c: OpRrcReg(self, 'h'),
            0x0d: OpRrcReg(self, 'l'),
            0x0e: OpRrcHlIndirect(self, self.memory),
            0x0f: OpRrcReg(self, 'a'),

            0x10: OpRlReg(self, 'b'),
            0x11: OpRlReg(self, 'c'),
            0x12: OpRlReg(self, 'd'),
            0x13: OpRlReg(self, 'e'),
            0x14: OpRlReg(self, 'h'),
            0x15: OpRlReg(self, 'l'),
            0x16: OpRlHlIndirect(self, self.memory),
            0x17: OpRlReg(self, 'a'),
            0x18: OpRrReg(self, 'b'),
            0x19: OpRrReg(self, 'c'),
            0x1a: OpRrReg(self, 'd'),
            0x1b: OpRrReg(self, 'e'),
            0x1c: OpRrReg(self, 'h'),
            0x1d: OpRrReg(self, 'l'),
            0x1e: OpRrHlIndirect(self, self.memory),
            0x1f: OpRrReg(self, 'a'),

            0x20: OpSlaReg(self, 'b'),
            0x21: OpSlaReg(self, 'c'),
            0x22: OpSlaReg(self, 'd'),
            0x23: OpSlaReg(self, 'e'),
            0x24: OpSlaReg(self, 'h'),
            0x25: OpSlaReg(self, 'l'),
            0x26: OpSlaHlIndirect(self, self.memory),
            0x27: OpSlaReg(self, 'a'),
            0x28: OpSraReg(self, 'b'),
            0x29: OpSraReg(self, 'c'),
            0x2a: OpSraReg(self, 'd'),
            0x2b: OpSraReg(self, 'e'),
            0x2c: OpSraReg(self, 'h'),
            0x2d: OpSraReg(self, 'l'),
            0x2e: OpSraHlIndirect(self, self.memory),
            0x2f: OpSraReg(self, 'a'),

            0x30: OpSllReg(self, 'b'),
            0x31: OpSllReg(self, 'c'),
            0x32: OpSllReg(self, 'd'),
            0x33: OpSllReg(self, 'e'),
            0x34: OpSllReg(self, 'h'),
            0x35: OpSllReg(self, 'l'),
            0x36: OpSllHlIndirect(self, self.memory),
            0x37: OpSllReg(self, 'a'),
            0x38: OpSrlReg(self, 'b'),
            0x39: OpSrlReg(self, 'c'),
            0x3a: OpSrlReg(self, 'd'),
            0x3b: OpSrlReg(self, 'e'),
            0x3c: OpSrlReg(self, 'h'),
            0x3d: OpSrlReg(self, 'l'),
            0x3e: OpSrlHlIndirect(self, self.memory),
            0x3f: OpSrlReg(self, 'a'),

            0x40: OpBitReg(self, 'b', 0),
            0x41: OpBitReg(self, 'c', 0),
            0x42: OpBitReg(self, 'd', 0),
            0x43: OpBitReg(self, 'e', 0),
            0x44: OpBitReg(self, 'h', 0),
            0x45: OpBitReg(self, 'l', 0),
            0x46: OpBitHlIndirect(self, self.memory, 0),
            0x47: OpBitReg(self, 'a', 0),
            0x48: OpBitReg(self, 'b', 1),
            0x49: OpBitReg(self, 'c', 1),
            0x4a: OpBitReg(self, 'd', 1),
            0x4b: OpBitReg(self, 'e', 1),
            0x4c: OpBitReg(self, 'h', 1),
            0x4d: OpBitReg(self, 'l', 1),
            0x4e: OpBitHlIndirect(self, self.memory, 1),
            0x4f: OpBitReg(self, 'a', 1),

            0x50: OpBitReg(self, 'b', 2),
            0x51: OpBitReg(self, 'c', 2),
            0x52: OpBitReg(self, 'd', 2),
            0x53: OpBitReg(self, 'e', 2),
            0x54: OpBitReg(self, 'h', 2),
            0x55: OpBitReg(self, 'l', 2),
            0x56: OpBitHlIndirect(self, self.memory, 2),
            0x57: OpBitReg(self, 'a', 2),
            0x58: OpBitReg(self, 'b', 3),
            0x59: OpBitReg(self, 'c', 3),
            0x5a: OpBitReg(self, 'd', 3),
            0x5b: OpBitReg(self, 'e', 3),
            0x5c: OpBitReg(self, 'h', 3),
            0x5d: OpBitReg(self, 'l', 3),
            0x5e: OpBitHlIndirect(self, self.memory, 3),
            0x5f: OpBitReg(self, 'a', 3),

            0x60: OpBitReg(self, 'b', 4),
            0x61: OpBitReg(self, 'c', 4),
            0x62: OpBitReg(self, 'd', 4),
            0x63: OpBitReg(self, 'e', 4),
            0x64: OpBitReg(self, 'h', 4),
            0x65: OpBitReg(self, 'l', 4),
            0x66: OpBitHlIndirect(self, self.memory, 4),
            0x67: OpBitReg(self, 'a', 4),
            0x68: OpBitReg(self, 'b', 5),
            0x69: OpBitReg(self, 'c', 5),
            0x6a: OpBitReg(self, 'd', 5),
            0x6b: OpBitReg(self, 'e', 5),
            0x6c: OpBitReg(self, 'h', 5),
            0x6d: OpBitReg(self, 'l', 5),
            0x6e: OpBitHlIndirect(self, self.memory, 5),
            0x6f: OpBitReg(self, 'a', 5),

            0x70: OpBitReg(self, 'b', 6),
            0x71: OpBitReg(self, 'c', 6),
            0x72: OpBitReg(self, 'd', 6),
            0x73: OpBitReg(self, 'e', 6),
            0x74: OpBitReg(self, 'h', 6),
            0x75: OpBitReg(self, 'l', 6),
            0x76: OpBitHlIndirect(self, self.memory, 6),
            0x77: OpBitReg(self, 'a', 6),
            0x78: OpBitReg(self, 'b', 7),
            0x79: OpBitReg(self, 'c', 7),
            0x7a: OpBitReg(self, 'd', 7),
            0x7b: OpBitReg(self, 'e', 7),
            0x7c: OpBitReg(self, 'h', 7),
            0x7d: OpBitReg(self, 'l', 7),
            0x7e: OpBitHlIndirect(self, self.memory, 7),
            0x7f: OpBitReg(self, 'a', 7),

            0x80: OpResReg(self, 'b', 0),
            0x81: OpResReg(self, 'c', 0),
            0x82: OpResReg(self, 'd', 0),
            0x83: OpResReg(self, 'e', 0),
            0x84: OpResReg(self, 'h', 0),
            0x85: OpResReg(self, 'l', 0),
            0x86: OpResHlIndirect(self, self.memory, 0),
            0x87: OpResReg(self, 'a', 0),
            0x88: OpResReg(self, 'b', 1),
            0x89: OpResReg(self, 'c', 1),
            0x8a: OpResReg(self, 'd', 1),
            0x8b: OpResReg(self, 'e', 1),
            0x8c: OpResReg(self, 'h', 1),
            0x8d: OpResReg(self, 'l', 1),
            0x8e: OpResHlIndirect(self, self.memory, 1),
            0x8f: OpResReg(self, 'a', 1),

            0x90: OpResReg(self, 'b', 2),
            0x91: OpResReg(self, 'c', 2),
            0x92: OpResReg(self, 'd', 2),
            0x93: OpResReg(self, 'e', 2),
            0x94: OpResReg(self, 'h', 2),
            0x95: OpResReg(self, 'l', 2),
            0x96: OpResHlIndirect(self, self.memory, 2),
            0x97: OpResReg(self, 'a', 2),
            0x98: OpResReg(self, 'b', 3),
            0x99: OpResReg(self, 'c', 3),
            0x9a: OpResReg(self, 'd', 3),
            0x9b: OpResReg(self, 'e', 3),
            0x9c: OpResReg(self, 'h', 3),
            0x9d: OpResReg(self, 'l', 3),
            0x9e: OpResHlIndirect(self, self.memory, 3),
            0x9f: OpResReg(self, 'a', 3),

            0xa0: OpResReg(self, 'b', 4),
            0xa1: OpResReg(self, 'c', 4),
            0xa2: OpResReg(self, 'd', 4),
            0xa3: OpResReg(self, 'e', 4),
            0xa4: OpResReg(self, 'h', 4),
            0xa5: OpResReg(self, 'l', 4),
            0xa6: OpResHlIndirect(self, self.memory, 4),
            0xa7: OpResReg(self, 'a', 4),
            0xa8: OpResReg(self, 'b', 5),
            0xa9: OpResReg(self, 'c', 5),
            0xaa: OpResReg(self, 'd', 5),
            0xab: OpResReg(self, 'e', 5),
            0xac: OpResReg(self, 'h', 5),
            0xad: OpResReg(self, 'l', 5),
            0xae: OpResHlIndirect(self, self.memory, 5),
            0xaf: OpResReg(self, 'a', 5),

            0xb0: OpResReg(self, 'b', 6),
            0xb1: OpResReg(self, 'c', 6),
            0xb2: OpResReg(self, 'd', 6),
            0xb3: OpResReg(self, 'e', 6),
            0xb4: OpResReg(self, 'h', 6),
            0xb5: OpResReg(self, 'l', 6),
            0xb6: OpResHlIndirect(self, self.memory, 6),
            0xb7: OpResReg(self, 'a', 6),
            0xb8: OpResReg(self, 'b', 7),
            0xb9: OpResReg(self, 'c', 7),
            0xba: OpResReg(self, 'd', 7),
            0xbb: OpResReg(self, 'e', 7),
            0xbc: OpResReg(self, 'h', 7),
            0xbd: OpResReg(self, 'l', 7),
            0xbe: OpResHlIndirect(self, self.memory, 7),
            0xbf: OpResReg(self, 'a', 7),

            0xc0: OpSetReg(self, 'b', 0),
            0xc1: OpSetReg(self, 'c', 0),
            0xc2: OpSetReg(self, 'd', 0),
            0xc3: OpSetReg(self, 'e', 0),
            0xc4: OpSetReg(self, 'h', 0),
            0xc5: OpSetReg(self, 'l', 0),
            0xc6: OpSetHlIndirect(self, self.memory, 0),
            0xc7: OpSetReg(self, 'a', 0),
            0xc8: OpSetReg(self, 'b', 1),
            0xc9: OpSetReg(self, 'c', 1),
            0xca: OpSetReg(self, 'd', 1),
            0xcb: OpSetReg(self, 'e', 1),
            0xcc: OpSetReg(self, 'h', 1),
            0xcd: OpSetReg(self, 'l', 1),
            0xce: OpSetHlIndirect(self, self.memory, 1),
            0xcf: OpSetReg(self, 'a', 1),

            0xd0: OpSetReg(self, 'b', 2),
            0xd1: OpSetReg(self, 'c', 2),
            0xd2: OpSetReg(self, 'd', 2),
            0xd3: OpSetReg(self, 'e', 2),
            0xd4: OpSetReg(self, 'h', 2),
            0xd5: OpSetReg(self, 'l', 2),
            0xd6: OpSetHlIndirect(self, self.memory, 2),
            0xd7: OpSetReg(self, 'a', 2),
            0xd8: OpSetReg(self, 'b', 3),
            0xd9: OpSetReg(self, 'c', 3),
            0xda: OpSetReg(self, 'd', 3),
            0xdb: OpSetReg(self, 'e', 3),
            0xdc: OpSetReg(self, 'h', 3),
            0xdd: OpSetReg(self, 'l', 3),
            0xde: OpSetHlIndirect(self, self.memory, 3),
            0xdf: OpSetReg(self, 'a', 3),

            0xe0: OpSetReg(self, 'b', 4),
            0xe1: OpSetReg(self, 'c', 4),
            0xe2: OpSetReg(self, 'd', 4),
            0xe3: OpSetReg(self, 'e', 4),
            0xe4: OpSetReg(self, 'h', 4),
            0xe5: OpSetReg(self, 'l', 4),
            0xe6: OpSetHlIndirect(self, self.memory, 4),
            0xe7: OpSetReg(self, 'a', 4),
            0xe8: OpSetReg(self, 'b', 5),
            0xe9: OpSetReg(self, 'c', 5),
            0xea: OpSetReg(self, 'd', 5),
            0xeb: OpSetReg(self, 'e', 5),
            0xec: OpSetReg(self, 'h', 5),
            0xed: OpSetReg(self, 'l', 5),
            0xee: OpSetHlIndirect(self, self.memory, 5),
            0xef: OpSetReg(self, 'a', 5),

            0xf0: OpSetReg(self, 'b', 6),
            0xf1: OpSetReg(self, 'c', 6),
            0xf2: OpSetReg(self, 'd', 6),
            0xf3: OpSetReg(self, 'e', 6),
            0xf4: OpSetReg(self, 'h', 6),
            0xf5: OpSetReg(self, 'l', 6),
            0xf6: OpSetHlIndirect(self, self.memory, 6),
            0xf7: OpSetReg(self, 'a', 6),
            0xf8: OpSetReg(self, 'b', 7),
            0xf9: OpSetReg(self, 'c', 7),
            0xfa: OpSetReg(self, 'd', 7),
            0xfb: OpSetReg(self, 'e', 7),
            0xfc: OpSetReg(self, 'h', 7),
            0xfd: OpSetReg(self, 'l', 7),
            0xfe: OpSetHlIndirect(self, self.memory, 7),
            0xff: OpSetReg(self, 'a', 7)
        }

    def init_ed_opcodes(self):
        op_neg = OpNeg(self)
        op_im0 = OpIm(self, 0)
        op_in_a_c = OpIn8RegC(self, self.io, 'a')
        op_retn = OpRetn(self)
        return {
            0x40: OpIn8RegC(self, self.io, 'b'),
            0x41: OpOutC8Reg(self, self.io, 'b'),
            0x42: OpSbcHl16Reg(self, 'bc'),
            0x43: OpLdAddress16Reg(self, self.memory, 'bc'),
            0x44: op_neg,
            0x45: op_retn,
            0x46: op_im0,
            0x47: OpLdIA(self),
            0x48: OpIn8RegC(self, self.io, 'c'),
            0x49: OpOutC8Reg(self, self.io, 'c'),
            0x4a: OpAdcHl16Reg(self, 'bc'),
            0x4b: OpLd16RegAddress(self, self.memory, 'bc'),
            0x4c: op_neg,
            0x4d: OpReti(self),
            0x4e: op_im0,
            0x4f: OpLdRA(self),

            0x50: OpIn8RegC(self, self.io, 'd'),
            0x51: OpOutC8Reg(self, self.io, 'd'),
            0x52: OpSbcHl16Reg(self, 'de'),
            0x53: OpLdAddress16Reg(self, self.memory, 'de'),
            0x54: op_neg,
            0x55: op_retn,
            0x56: OpIm(self, 1),
            0x57: OpLdAI(self),
            0x58: OpIn8RegC(self, self.io, 'e'),
            0x59: OpOutC8Reg(self, self.io, 'e'),
            0x5a: OpAdcHl16Reg(self, 'de'),
            0x5b: OpLd16RegAddress(self, self.memory, 'de'),
            0x5c: op_neg,
            0x5d: op_retn,
            0x5e: OpIm(self, 2),
            0x5f: OpLdAR(self),

            0x60: OpIn8RegC(self, self.io, 'h'),
            0x61: OpOutC8Reg(self, self.io, 'h'),
            0x62: OpSbcHl16Reg(self, 'hl'),
            0x63: OpLdAddress16Reg(self, self.memory, 'hl'),
            0x64: op_neg,
            0x65: op_retn,
            0x66: OpIm(self, 0),
            0x67: OpRrd(self, self.memory),
            0x68: OpIn8RegC(self, self.io, 'l'),
            0x69: OpOutC8Reg(self, self.io, 'l'),
            0x6a: OpAdcHl16Reg(self, 'hl'),
            0x6b: OpLd16RegAddress(self, self.memory, 'hl'),
            0x6c: op_neg,
            0x6d: op_retn,
            0x6e: op_im0,
            0x6f: OpRld(self, self.memory),

            0x70: op_in_a_c,
            0x71: OpOutCZero(self, self.io),
            0x72: OpSbcHl16Reg(self, 'sp'),
            0x73: OpLdExtSp(self, self.memory),
            0x74: op_neg,
            0x75: op_retn,
            0x76: OpIm(self, 1),
            0x78: op_in_a_c,
            0x79: OpOutC8Reg(self, self.io, 'a'),
            0x7a: OpAdcHl16Reg(self, 'sp'),
            0x7b: OpLdSpExt(self, self.memory),
            0x7c: op_neg,
            0x7d: op_retn,
            0x7e: OpIm(self, 2),

            0xa0: OpLdi(self, self.memory),
            0xa1: OpCpi(self, self.memory),
            0xa2: OpIni(self, self.memory, self.io),
            0xa3: OpOuti(self, self.memory, self.io),
            0xa8: OpLdd(self, self.memory),
            0xa9: OpCpd(self, self.memory),
            0xaa: OpInd(self, self.memory, self.io),
            0xab: OpOutd(self, self.memory, self.io),

            0xb0: OpLdir(self, self.memory),
            0xb1: OpCpir(self, self.memory),
            0xb2: OpInir(self, self.memory, self.io),
            0xb3: OpOtir(self, self.memory, self.io),
            0xb8: OpLddr(self, self.memory),
            0xb9: OpCpdr(self, self.memory),
            0xba: OpIndr(self, self.memory, self.io),
            0xbb: OpOtdr(self, self.memory, self.io)
        }

    def init_dd_opcodes(self):
        return {
            0x09: OpAddIndexedReg(self, 'ix', 'bc'),

            0x19: OpAddIndexedReg(self, 'ix', 'de'),

            0x21: OpLdIndexedImmediate(self, 'ix'),
            0x22: OpLdExtIndexed(self, self.memory, 'ix'),
            0x23: OpIncIndexed(self, 'ix'),
            0x24: Undocumented('inc ixh'),
            0x25: Undocumented('dec ixh'),
            0x26: Undocumented('ld ixh, n'),
            0x29: OpAddIndexedReg(self, 'ix', 'ix'),
            0x2a: OpLdIndexedExt(self, self.memory, 'ix'),
            0x2b: OpDecIndexed(self, 'ix'),
            0x2c: Undocumented('inc ixl'),
            0x2d: Undocumented('dec ixl'),
            0x2e: Undocumented('ld ixl, n'),

            0x34: OpIncIndexedIndirect(self, self.memory, 'ix'),
            0x35: OpDecIndexedIndirect(self, self.memory, 'ix'),
            0x36: OpLdIndexedIndirectImmediate(self, self.memory, 'ix'),
            0x39: OpAddIndexedReg(self, 'ix', 'sp'),

            0x44: Undocumented('ld b, ixh'),
            0x45: Undocumented('ld b, ixl'),
            0x46: OpLd8RegIndexedIndirect(self, self.memory, 'b', 'ix'),
            0x4c: Undocumented('ld c, ixh'),
            0x4d: Undocumented('ld c, ixl'),
            0x4e: OpLd8RegIndexedIndirect(self, self.memory, 'c', 'ix'),

            0x54: Undocumented('ld d, ixh'),
            0x55: Undocumented('ld d, ixl'),
            0x56: OpLd8RegIndexedIndirect(self, self.memory, 'd', 'ix'),
            0x5c: Undocumented('ld e, ixh'),
            0x5d: Undocumented('ld e, ixl'),
            0x5e: OpLd8RegIndexedIndirect(self, self.memory, 'e', 'ix'),

            0x60: Undocumented('ld ixh, b'),
            0x61: Undocumented('ld ixh, c'),
            0x62: Undocumented('ld ixh, d'),
            0x63: Undocumented('ld ixh, e'),
            0x64: Undocumented('ld ixh, h'),
            0x65: Undocumented('ld ixh, l'),
            0x66: OpLd8RegIndexedIndirect(self, self.memory, 'h', 'ix'),
            0x67: Undocumented('ld ixl, a'),
            0x68: Undocumented('ld ixl, b'),
            0x69: Undocumented('ld ixl, c'),
            0x6a: Undocumented('ld ixl, d'),
            0x6b: Undocumented('ld ixl, e'),
            0x6c: Undocumented('ld ixl, h'),
            0x6d: Undocumented('ld ixl, l'),
            0x6e: OpLd8RegIndexedIndirect(self, self.memory, 'l', 'ix'),
            0x6f: Undocumented('ld ixl, a'),

            0x70: OpLdIndexedIndirect8Reg(self, self.memory, 'ix', 'b'),
            0x71: OpLdIndexedIndirect8Reg(self, self.memory, 'ix', 'c'),
            0x72: OpLdIndexedIndirect8Reg(self, self.memory, 'ix', 'd'),
            0x73: OpLdIndexedIndirect8Reg(self, self.memory, 'ix', 'e'),
            0x74: OpLdIndexedIndirect8Reg(self, self.memory, 'ix', 'h'),
            0x75: OpLdIndexedIndirect8Reg(self, self.memory, 'ix', 'l'),
            0x77: OpLdIndexedIndirect8Reg(self, self.memory, 'ix', 'a'),
            0x7c: Undocumented('ld a, ixh'),
            0x7d: Undocumented('ld a, ixl'),
            0x7e: OpLd8RegIndexedIndirect(self, self.memory, 'a', 'ix'),

            0x84: Undocumented('add a, ixh'),
            0x85: Undocumented('add a, ixl'),
            0x86: OpAddAIndexedIndirect(self, self.memory, 'ix'),
            0x8c: Undocumented('adc a, ixh'),
            0x8d: Undocumented('adc a, ixl'),
            0x8e: OpAdcAIndexedIndirect(self, self.memory, 'ix'),

            0x94: Undocumented('sub ixh'),
            0x95: Undocumented('sub ixl'),
            0x96: OpSubAIndexedIndirect(self, self.memory, 'ix'),
            0x9c: Undocumented('sbc a, ixh'),
            0x9d: Undocumented('sbc a, ixl'),
            0x9e: OpSbcAIndexedIndirect(self, self.memory, 'ix'),

            0xa4: Undocumented('and ixh'),
            0xa5: Undocumented('and ixl'),
            0xa6: OpAndIndexedIndirect(self, self.memory, 'ix'),
            0xac: Undocumented('xor a, ixh'),
            0xad: Undocumented('xor a, ixl'),
            0xae: OpXorIndexedIndirect(self, self.memory, 'ix'),

            0xb4: Undocumented('or ixh'),
            0xb5: Undocumented('or ixl'),
            0xb6: OpOrIndexedIndirect(self, self.memory, 'ix'),
            0xbc: Undocumented('cp ixh'),
            0xbd: Undocumented('cp ixl'),
            0xbe: OpCpIndexedIndirect(self, self.memory, 'ix'),

            0xcb: self.init_indexed_cb_opcodes('ix'),

            0xe1: OpPopIndexed(self, 'ix'),
            0xe3: OpExSpIndirectIndexed(self, self.memory, 'ix'),
            0xe5: OpPushIndexed(self, 'ix'),
            0xe9: OpJpIndexedIndirect(self, 'ix'),

            0xf9: OpLdSpIndexed(self, 'ix'),
        }

    def init_fd_opcodes(self):
        return {
            0x09: OpAddIndexedReg(self, 'iy', 'bc'),

            0x19: OpAddIndexedReg(self, 'iy', 'de'),

            0x21: OpLdIndexedImmediate(self, 'iy'),
            0x22: OpLdExtIndexed(self, self.memory, 'iy'),
            0x23: OpIncIndexed(self, 'iy'),
            0x24: Undocumented('inc iyh'),
            0x25: Undocumented('dec iyh'),
            0x26: Undocumented('ld iyh, n'),
            0x29: OpAddIndexedReg(self, 'iy', 'iy'),
            0x2a: OpLdIndexedExt(self, self.memory, 'iy'),
            0x2b: OpDecIndexed(self, 'iy'),
            0x2c: Undocumented('inc iyl'),
            0x2d: Undocumented('dec iyl'),
            0x2e: Undocumented('ld iyl, n'),

            0x34: OpIncIndexedIndirect(self, self.memory, 'iy'),
            0x35: OpDecIndexedIndirect(self, self.memory, 'iy'),
            0x36: OpLdIndexedIndirectImmediate(self, self.memory, 'iy'),
            0x39: OpAddIndexedReg(self, 'iy', 'sp'),

            0x44: Undocumented('ld b, iyh'),
            0x45: Undocumented('ld b, iyl'),
            0x46: OpLd8RegIndexedIndirect(self, self.memory, 'b', 'iy'),
            0x4c: Undocumented('ld c, iyh'),
            0x4d: Undocumented('ld c, iyl'),
            0x4e: OpLd8RegIndexedIndirect(self, self.memory, 'c', 'iy'),

            0x54: Undocumented('ld d, iyh'),
            0x55: Undocumented('ld d, iyl'),
            0x56: OpLd8RegIndexedIndirect(self, self.memory, 'd', 'iy'),
            0x5c: Undocumented('ld e, iyh'),
            0x5d: Undocumented('ld e, iyl'),
            0x5e: OpLd8RegIndexedIndirect(self, self.memory, 'e', 'iy'),

            0x60: Undocumented('ld iyh, b'),
            0x61: Undocumented('ld iyh, c'),
            0x62: Undocumented('ld iyh, d'),
            0x63: Undocumented('ld iyh, e'),
            0x64: Undocumented('ld iyh, h'),
            0x65: Undocumented('ld iyh, l'),
            0x66: OpLd8RegIndexedIndirect(self, self.memory, 'h', 'iy'),
            0x67: Undocumented('ld iyl, a'),
            0x68: Undocumented('ld iyl, b'),
            0x69: Undocumented('ld iyl, c'),
            0x6a: Undocumented('ld iyl, d'),
            0x6b: Undocumented('ld iyl, e'),
            0x6c: Undocumented('ld iyl, h'),
            0x6d: Undocumented('ld iyl, l'),
            0x6e: OpLd8RegIndexedIndirect(self, self.memory, 'l', 'iy'),
            0x6f: Undocumented('ld iyl, a'),

            0x70: OpLdIndexedIndirect8Reg(self, self.memory, 'iy', 'b'),
            0x71: OpLdIndexedIndirect8Reg(self, self.memory, 'iy', 'c'),
            0x72: OpLdIndexedIndirect8Reg(self, self.memory, 'iy', 'd'),
            0x73: OpLdIndexedIndirect8Reg(self, self.memory, 'iy', 'e'),
            0x74: OpLdIndexedIndirect8Reg(self, self.memory, 'iy', 'h'),
            0x75: OpLdIndexedIndirect8Reg(self, self.memory, 'iy', 'l'),
            0x77: OpLdIndexedIndirect8Reg(self, self.memory, 'iy', 'a'),
            0x7c: Undocumented('ld a, iyh'),
            0x7d: Undocumented('ld a, iyl'),
            0x7e: OpLd8RegIndexedIndirect(self, self.memory, 'a', 'iy'),

            0x84: Undocumented('add a, iyh'),
            0x85: Undocumented('add a, iyl'),
            0x86: OpAddAIndexedIndirect(self, self.memory, 'iy'),
            0x8c: Undocumented('adc a, iyh'),
            0x8d: Undocumented('adc a, iyl'),
            0x8e: OpAdcAIndexedIndirect(self, self.memory, 'iy'),

            0x94: Undocumented('sub iyh'),
            0x95: Undocumented('sub iyl'),
            0x96: OpSubAIndexedIndirect(self, self.memory, 'iy'),
            0x9c: Undocumented('sbc a, iyh'),
            0x9d: Undocumented('sbc a, iyl'),
            0x9e: OpSbcAIndexedIndirect(self, self.memory, 'iy'),

            0xa4: Undocumented('and iyh'),
            0xa5: Undocumented('and iyl'),
            0xa6: OpAndIndexedIndirect(self, self.memory, 'iy'),
            0xac: Undocumented('xor a, iyh'),
            0xad: Undocumented('xor a, iyl'),
            0xae: OpXorIndexedIndirect(self, self.memory, 'iy'),

            0xb4: Undocumented('or iyh'),
            0xb5: Undocumented('or iyl'),
            0xb6: OpOrIndexedIndirect(self, self.memory, 'iy'),
            0xbc: Undocumented('cp iyh'),
            0xbd: Undocumented('cp iyl'),
            0xbe: OpCpIndexedIndirect(self, self.memory, 'iy'),

            0xcb: self.init_indexed_cb_opcodes('iy'),

            0xe1: OpPopIndexed(self, 'iy'),
            0xe3: OpExSpIndirectIndexed(self, self.memory, 'iy'),
            0xe5: OpPushIndexed(self, 'iy'),
            0xe9: OpJpIndexedIndirect(self, 'iy'),

            0xf9: OpLdSpIndexed(self, 'iy'),
        }

    def init_indexed_cb_opcodes(self, reg):
        return {
            0x06: OpRlcIndexedIndirect(self, self.memory, reg),
            0x0e: OpRrcIndexedIndirect(self, self.memory, reg),
            0x16: OpRlIndexedIndirect(self, self.memory, reg),
            0x1e: OpRrIndexedIndirect(self, self.memory, reg),
            0x26: OpSlaIndexedIndirect(self, self.memory, reg),
            0x2e: OpSraIndexedIndirect(self, self.memory, reg),
            0x3e: OpSrlIndexedIndirect(self, self.memory, reg),

            0x46: OpBitIndexedIndirect(self, self.memory, reg, 0),
            0x4e: OpBitIndexedIndirect(self, self.memory, reg, 1),
            0x56: OpBitIndexedIndirect(self, self.memory, reg, 2),
            0x5e: OpBitIndexedIndirect(self, self.memory, reg, 3),
            0x66: OpBitIndexedIndirect(self, self.memory, reg, 4),
            0x6e: OpBitIndexedIndirect(self, self.memory, reg, 5),
            0x76: OpBitIndexedIndirect(self, self.memory, reg, 6),
            0x7e: OpBitIndexedIndirect(self, self.memory, reg, 7),

            0x86: OpResIndexedIndirect(self, self.memory, reg, 0),
            0x8e: OpResIndexedIndirect(self, self.memory, reg, 1),
            0x96: OpResIndexedIndirect(self, self.memory, reg, 2),
            0x9e: OpResIndexedIndirect(self, self.memory, reg, 3),
            0xa6: OpResIndexedIndirect(self, self.memory, reg, 4),
            0xae: OpResIndexedIndirect(self, self.memory, reg, 5),
            0xb6: OpResIndexedIndirect(self, self.memory, reg, 6),
            0xbe: OpResIndexedIndirect(self, self.memory, reg, 7),

            0xc6: OpSetIndexedIndirect(self, self.memory, reg, 0),
            0xce: OpSetIndexedIndirect(self, self.memory, reg, 1),
            0xd6: OpSetIndexedIndirect(self, self.memory, reg, 2),
            0xde: OpSetIndexedIndirect(self, self.memory, reg, 3),
            0xe6: OpSetIndexedIndirect(self, self.memory, reg, 4),
            0xee: OpSetIndexedIndirect(self, self.memory, reg, 5),
            0xf6: OpSetIndexedIndirect(self, self.memory, reg, 6),
            0xfe: OpSetIndexedIndirect(self, self.memory, reg, 7),
        }

    def set_iff(self):
        self.iff[0] = True
        self.iff[1] = True

    def nmi(self):
        self.halting = False
        self.iff[0] = False
        self.push_pc()
        self.special_registers['pc'] = 0x0066

    def set_interrupt_mode(self, interrupt_mode):
        self.interrupt_mode = interrupt_mode

    def interrupt(self, interrupt_request):
        self.interrupt_requests.append(interrupt_request)

    def push_pc(self):
        high_byte, low_byte = high_low_pair(self.special_registers['pc'])
        self.push_byte(high_byte)
        self.push_byte(low_byte)

    def execute(self):
        enable_iff_after_op = self.enable_iff
        operation = self.get_operation()
        self.increment_r()
        if not isinstance(operation, Op):
            operation.execute()
        else:
            operation.function()
        if enable_iff_after_op:
            self.set_iff()
            self.enable_iff = False
        return operation

    def increment_r(self):
        high_bit = self.special_registers['r'] & 0b10000000
        low_bits = self.special_registers['r'] & 0b01111111
        low_bits = low_bits + 1
        self.special_registers['r'] = high_bit | (low_bits & 0b01111111)

    def get_operation(self):
        if self.iff[0] and len(self.interrupt_requests) > 0:
            self.halting = False
            next_request = self.interrupt_requests.pop(0)
            next_request.acknowledge()
            if self.interrupt_mode == 0:
                self.push_pc()
                self.interrupt_data_queue = next_request.get_im0_data()
            elif self.interrupt_mode == 1:
                return self.im1_response_op
            elif self.interrupt_mode == 2:
                table_index = big_endian_value([self.special_registers['r'] & 0xfe, self.special_registers['i']])
                jump_low_byte = self.memory.peek(table_index)
                jump_high_byte = self.memory.peek(table_index + 1)
                return OpCallDirect(self, big_endian_value([jump_low_byte, jump_high_byte]))

        if self.halting:
            op_code = 0x00
        else:
            op_code = self.get_next_byte()

        operation = self.operations_by_opcode[op_code]
        if isinstance(operation, dict):
            op_code = self.get_next_byte()
            operation = operation[op_code]
            if isinstance(operation, dict):
                self.get_next_byte()
                op_code = self.get_next_byte()
                operation = operation[op_code]

        return operation

    def get_address_at_pc(self):
        return [self.get_next_byte(), self.get_next_byte()]

    def get_next_byte(self):
        if len(self.interrupt_data_queue) > 0:
            return self.interrupt_data_queue.pop(0)
        else:
            op_code = self.memory.peek(self.special_registers['pc'])
            self.increment('pc')
            return op_code

    def get_signed_offset_byte(self):
        return to_signed(self.memory.peek(self.special_registers['pc'] - 2))

    def restore_pc_from_stack(self):
        self.special_registers['pc'] = self._get_destination_from_stack()

    def _get_destination_from_stack(self):
        return big_endian_value([self.pop_byte(), self.pop_byte()])

    def increment(self, register_name):
        self.special_registers[register_name] += 1

    def push_byte(self, byte):
        if self.special_registers['sp'] == 0:
            self.special_registers['sp'] = 0xffff
        else:
            self.special_registers['sp'] -= 1
        self.memory.poke(self.special_registers['sp'], byte)

    def pop_byte(self):
        byte = self.memory.peek(self.special_registers['sp'])
        if self.special_registers['sp'] == 0xffff:
            self.special_registers['sp'] = 0
        else:
            self.special_registers['sp'] += 1
        return byte

    def set_condition(self, flag, value):
        mask = self.condition_masks[flag]
        if value:
            self.main_registers['f'] |= mask
        else:
            self.main_registers['f'] &= (0xff ^ mask)

    def condition(self, flag):
        mask = self.condition_masks[flag]
        return self.main_registers['f'] & mask > 0

    def get_16bit_reg(self, register_pair):
        if register_pair == 'sp':
            return self.special_registers['sp']
        elif register_pair == 'ix' or register_pair == 'iy':
            return self.index_registers[register_pair]
        else:
            msb = self.main_registers[register_pair[0]]
            lsb = self.main_registers[register_pair[1]]
            return big_endian_value([lsb, msb])

    def set_16bit_reg(self, register_pair, val_16bit):
        if register_pair == 'sp':
            self.special_registers['sp'] = val_16bit
        else:
            high_byte, low_byte = high_low_pair(val_16bit)
            self.main_registers[register_pair[0]] = high_byte
            self.main_registers[register_pair[1]] = low_byte

    def get_16bit_alt_reg(self, register_pair):
        msb = self.alternate_registers[register_pair[0]]
        lsb = self.alternate_registers[register_pair[1]]
        return big_endian_value([lsb, msb])


class InterruptRequest:
    def __init__(self, acknowledge_cb, get_im0_data = None):
        self.acknowledge_cb = acknowledge_cb
        self.get_im0_data = get_im0_data
        self.cancelled = False

    def acknowledge(self):
        self.acknowledge_cb()

    def cancel(self):
        self.cancelled = True