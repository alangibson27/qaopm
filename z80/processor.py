from bit import *
from call import *
from jump import *
from rotate import *
from shift import *
from arithmetic_16 import *
from funcs import *
from ld_operations import *
from inc_operations import *
from exchange_operations import *
from z80.arithmetic_8 import *
from stack import *


class Op:
    def __init__(self, function, mnemonic):
        self.function = function
        self.mnemonic = mnemonic


class Processor:
    def __init__(self, memory):
        self.memory = memory
        self.main_registers = self.build_swappable_register_set()
        self.alternate_registers = self.build_swappable_register_set()
        self.special_registers = self.build_special_register_set()
        self.index_registers = self.build_index_register_set()
        self.operations_by_opcode = self.init_opcode_map()
        self.cycles = 0
        self.enable_iff = False
        self.iff = [False, False]
        self.interrupt_data_queue = []
        self.interrupt_mode = 0
        self.interrupt_requests = []
        self.halting = False
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

    def create_ld_reg_from_reg_indirect(self, destination, source_register):
        return Op(lambda: self.ld_reg_from_reg_indirect(destination, source_register),
                  'ld {}, ({})'.format(destination, source_register))

    def create_ld_reg_indirect_from_reg(self, destination_register, source_register):
        return Op(lambda: self.ld_reg_indirect_from_reg(destination_register, source_register),
                  'ld ({}), {}'.format(destination_register, source_register))

    def init_opcode_map(self):
        return {
            0x00: Op(self.nop, 'nop'),

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
            0x22: OpLdAddress16Reg(self, self.memory, 'hl'),
            0x23: OpInc16Reg(self, 'hl'),
            0x24: OpInc8Reg(self, 'h'),
            0x25: OpDec8Reg(self, 'h'),
            0x26: OpLd8RegImmediate(self, 'h'),
            0x27: OpDaa(self),
            0x28: OpJrZ(self),
            0x29: OpAddHl16Reg(self, 'hl'),
            0x2a: OpLd16RegAddress(self, self.memory, 'hl'),
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
            0x76: Op(self.halt, 'halt'),
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
            0xd4: OpCallNc(self),
            0xd5: OpPush16Reg(self, 'de'),
            0xd6: OpSubAImmediate(self, self.memory),
            0xd7: OpRst(self, 0x10),
            0xd8: OpRetC(self),
            0xd9: OpExx(self),
            0xda: OpJpC(self),
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
            0xf3: Op(self.di, 'di'),
            0xf4: OpCallP(self),
            0xf5: OpPush16Reg(self, 'af'),
            0xf6: OpOrAImmediate(self),
            0xf7: OpRst(self, 0x30),
            0xf8: OpRetM(self),
            0xf9: OpLdSpHl(self),
            0xfa: OpJpM(self),
            0xfb: Op(self.ei, 'ei'),
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

            0xc0: Op(lambda: set_reg(self, 'b', 0), 'set 0, b'),
            0xc1: Op(lambda: set_reg(self, 'c', 0), 'set 0, c'),
            0xc2: Op(lambda: set_reg(self, 'd', 0), 'set 0, d'),
            0xc3: Op(lambda: set_reg(self, 'e', 0), 'set 0, e'),
            0xc4: Op(lambda: set_reg(self, 'h', 0), 'set 0, h'),
            0xc5: Op(lambda: set_reg(self, 'l', 0), 'set 0, l'),
            0xc6: Op(lambda: set_hl_indirect(self, self.memory, 0), 'set 0, (hl)'),
            0xc7: Op(lambda: set_reg(self, 'a', 0), 'set 0, a'),

            0xc8: Op(lambda: set_reg(self, 'b', 1), 'set 1, b'),
            0xc9: Op(lambda: set_reg(self, 'c', 1), 'set 1, c'),
            0xca: Op(lambda: set_reg(self, 'd', 1), 'set 1, d'),
            0xcb: Op(lambda: set_reg(self, 'e', 1), 'set 1, e'),
            0xcc: Op(lambda: set_reg(self, 'h', 1), 'set 1, h'),
            0xcd: Op(lambda: set_reg(self, 'l', 1), 'set 1, l'),
            0xce: Op(lambda: set_hl_indirect(self, self.memory, 1), 'set 1, (hl)'),
            0xcf: Op(lambda: set_reg(self, 'a', 1), 'set 1, a'),

            0xd0: Op(lambda: set_reg(self, 'b', 2), 'set 2, b'),
            0xd1: Op(lambda: set_reg(self, 'c', 2), 'set 2, c'),
            0xd2: Op(lambda: set_reg(self, 'd', 2), 'set 2, d'),
            0xd3: Op(lambda: set_reg(self, 'e', 2), 'set 2, e'),
            0xd4: Op(lambda: set_reg(self, 'h', 2), 'set 2, h'),
            0xd5: Op(lambda: set_reg(self, 'l', 2), 'set 2, l'),
            0xd6: Op(lambda: set_hl_indirect(self, self.memory, 2), 'set 2, (hl)'),
            0xd7: Op(lambda: set_reg(self, 'a', 2), 'set 2, a'),

            0xd8: Op(lambda: set_reg(self, 'b', 3), 'set 3, b'),
            0xd9: Op(lambda: set_reg(self, 'c', 3), 'set 3, c'),
            0xda: Op(lambda: set_reg(self, 'd', 3), 'set 3, d'),
            0xdb: Op(lambda: set_reg(self, 'e', 3), 'set 3, e'),
            0xdc: Op(lambda: set_reg(self, 'h', 3), 'set 3, h'),
            0xdd: Op(lambda: set_reg(self, 'l', 3), 'set 3, l'),
            0xde: Op(lambda: set_hl_indirect(self, self.memory, 3), 'set 3, (hl)'),
            0xdf: Op(lambda: set_reg(self, 'a', 3), 'set 3, a'),

            0xe0: Op(lambda: set_reg(self, 'b', 4), 'set 4, b'),
            0xe1: Op(lambda: set_reg(self, 'c', 4), 'set 4, c'),
            0xe2: Op(lambda: set_reg(self, 'd', 4), 'set 4, d'),
            0xe3: Op(lambda: set_reg(self, 'e', 4), 'set 4, e'),
            0xe4: Op(lambda: set_reg(self, 'h', 4), 'set 4, h'),
            0xe5: Op(lambda: set_reg(self, 'l', 4), 'set 4, l'),
            0xe6: Op(lambda: set_hl_indirect(self, self.memory, 4), 'set 4, (hl)'),
            0xe7: Op(lambda: set_reg(self, 'a', 4), 'set 4, a'),

            0xe8: Op(lambda: set_reg(self, 'b', 5), 'set 5, b'),
            0xe9: Op(lambda: set_reg(self, 'c', 5), 'set 5, c'),
            0xea: Op(lambda: set_reg(self, 'd', 5), 'set 5, d'),
            0xeb: Op(lambda: set_reg(self, 'e', 5), 'set 5, e'),
            0xec: Op(lambda: set_reg(self, 'h', 5), 'set 5, h'),
            0xed: Op(lambda: set_reg(self, 'l', 5), 'set 5, l'),
            0xee: Op(lambda: set_hl_indirect(self, self.memory, 5), 'set 5, (hl)'),
            0xef: Op(lambda: set_reg(self, 'a', 5), 'set 5, a'),

            0xf0: Op(lambda: set_reg(self, 'b', 6), 'set 6, b'),
            0xf1: Op(lambda: set_reg(self, 'c', 6), 'set 6, c'),
            0xf2: Op(lambda: set_reg(self, 'd', 6), 'set 6, d'),
            0xf3: Op(lambda: set_reg(self, 'e', 6), 'set 6, e'),
            0xf4: Op(lambda: set_reg(self, 'h', 6), 'set 6, h'),
            0xf5: Op(lambda: set_reg(self, 'l', 6), 'set 6, l'),
            0xf6: Op(lambda: set_hl_indirect(self, self.memory, 6), 'set 6, (hl)'),
            0xf7: Op(lambda: set_reg(self, 'a', 6), 'set 6, a'),

            0xf8: Op(lambda: set_reg(self, 'b', 7), 'set 7, b'),
            0xf9: Op(lambda: set_reg(self, 'c', 7), 'set 7, c'),
            0xfa: Op(lambda: set_reg(self, 'd', 7), 'set 7, d'),
            0xfb: Op(lambda: set_reg(self, 'e', 7), 'set 7, e'),
            0xfc: Op(lambda: set_reg(self, 'h', 7), 'set 7, h'),
            0xfd: Op(lambda: set_reg(self, 'l', 7), 'set 7, l'),
            0xfe: Op(lambda: set_hl_indirect(self, self.memory, 7), 'set 7, (hl)'),
            0xff: Op(lambda: set_reg(self, 'a', 7), 'set 7, a')
        }

    def init_ed_opcodes(self):
        return {
            0x42: Op(lambda: sbc_hl_reg(self, 'bc'), 'sbc hl, bc'),
            0x43: OpLdAddress16Reg(self, self.memory, 'bc'),
            0x44: Op(self.neg, 'neg'),
            0x45: Op(self.retn, 'retn'),
            0x46: Op(lambda: self.set_interrupt_mode(0), 'im 0'),
            0x4a: Op(lambda: adc_hl_reg(self, 'bc'), 'adc hl, bc'),
            0x4b: OpLd16RegAddress(self, self.memory, 'bc'),
            0x4d: Op(self.reti, 'reti'),

            0x52: Op(lambda: sbc_hl_reg(self, 'de'), 'sbc hl, de'),
            0x53: OpLdAddress16Reg(self, self.memory, 'de'),
            0x56: Op(lambda: self.set_interrupt_mode(1), 'im 1'),
            0x5a: Op(lambda: adc_hl_reg(self, 'de'), 'adc hl, de'),
            0x5b: OpLd16RegAddress(self, self.memory, 'de'),
            0x5e: Op(lambda: self.set_interrupt_mode(2), 'im 2'),

            0x62: Op(lambda: sbc_hl_reg(self, 'hl'), 'sbc hl, hl'),
            0x63: OpLdAddress16Reg(self, self.memory, 'hl'),
            0x66: Op(lambda: self.set_interrupt_mode(0), 'im 0'),
            0x67: Op(lambda: rrd(self, self.memory), 'rrd'),
            0x6a: Op(lambda: adc_hl_reg(self, 'hl'), 'adc hl, hl'),
            0x6b: OpLd16RegAddress(self, self.memory, 'hl'),
            0x6f: Op(lambda: rld(self, self.memory), 'rld'),

            0x72: Op(lambda: sbc_hl_reg(self, 'sp'), 'sbc hl, sp'),
            0x73: Op(lambda: self.ld_ext_sp(), 'ld (nn), sp'),
            0x76: Op(lambda: self.set_interrupt_mode(1), 'im 1'),
            0x7a: Op(lambda: adc_hl_reg(self, 'sp'), 'adc hl, sp'),
            0x7b: Op(lambda: self.ld_sp_ext(), 'ld sp, (nn)'),
            0x7e: Op(lambda: self.set_interrupt_mode(2), 'im 2'),

            0x57: Op(self.ld_a_i, 'ld a, i'),

            0xa0: Op(self.ldi, 'ldi'),
            0xa1: Op(self.cpi, 'cpi'),
            0xa8: Op(self.ldd, 'ldd'),
            0xa9: Op(self.cpd, 'cpd'),

            0xb0: Op(self.ldir, 'ldir'),
            0xb1: Op(self.cpir, 'cpir'),
            0xb8: Op(self.lddr, 'lddr'),
            0xb9: Op(self.cpdr, 'cpdr')
        }

    def init_dd_opcodes(self):
        return {
            0x09: Op(lambda: add_indexed_reg(self, 'ix', 'bc'), 'add ix, bc'),
            0x19: Op(lambda: add_indexed_reg(self, 'ix', 'de'), 'add ix, de'),
            0x21: Op(lambda: self.ld_indexed_reg_immediate('ix'), 'ld ix, nn'),
            0x22: Op(lambda: self.ld_ext_indexed_16reg('ix'), 'ld (nn), ix'),
            0x23: Op(lambda: inc_indexed_reg(self, 'ix'), 'inc ix'),
            0x29: Op(lambda: add_indexed_reg(self, 'ix', 'ix'), 'add ix, ix'),
            0x2a: Op(lambda: self.ld_indexed_16reg_ext('ix'), 'ld ix, (nn)'),
            0x2b: Op(lambda: dec_indexed_reg(self, 'ix'), 'dec ix'),
            0x34: Op(lambda: self.inc_indexed_indirect('ix'), 'inc (ix + d)'),
            0x35: Op(lambda: self.dec_indexed_indirect('ix'), 'dec (ix + d)'),
            0x36: Op(lambda: self.ld_indexed_addr_immediate('ix'), 'ld (ix + d), n'),
            0x39: Op(lambda: add_indexed_reg(self, 'ix', 'sp'), 'add ix, sp'),
            0x46: Op(lambda: self.ld_reg_indexed_addr('b', 'ix'), 'ld b, (ix + d)'),
            0x4e: Op(lambda: self.ld_reg_indexed_addr('c', 'ix'), 'ld c, (ix + d)'),
            0x56: Op(lambda: self.ld_reg_indexed_addr('d', 'ix'), 'ld d, (ix + d)'),
            0x5e: Op(lambda: self.ld_reg_indexed_addr('e', 'ix'), 'ld e, (ix + d)'),
            0x66: Op(lambda: self.ld_reg_indexed_addr('h', 'ix'), 'ld h, (ix + d)'),
            0x6e: Op(lambda: self.ld_reg_indexed_addr('l', 'ix'), 'ld l, (ix + d)'),
            0x70: Op(lambda: self.ld_indexed_reg_from_reg('ix', 'b'), 'ld (ix + d), b'),
            0x71: Op(lambda: self.ld_indexed_reg_from_reg('ix', 'c'), 'ld (ix + d), c'),
            0x72: Op(lambda: self.ld_indexed_reg_from_reg('ix', 'd'), 'ld (ix + d), d'),
            0x73: Op(lambda: self.ld_indexed_reg_from_reg('ix', 'e'), 'ld (ix + d), e'),
            0x74: Op(lambda: self.ld_indexed_reg_from_reg('ix', 'h'), 'ld (ix + d), h'),
            0x75: Op(lambda: self.ld_indexed_reg_from_reg('ix', 'l'), 'ld (ix + d), l'),
            0x77: Op(lambda: self.ld_indexed_reg_from_reg('ix', 'a'), 'ld (ix + d), a'),
            0x7e: Op(lambda: self.ld_reg_indexed_addr('a', 'ix'), 'ld a, (ix + d)'),

            0x86: Op(lambda: self.add_a_indexed_indirect('ix'), 'add a, (ix + d)'),
            0x8e: Op(lambda: self.adc_a_indexed_indirect('ix'), 'adc a, (ix + d)'),

            0x96: Op(lambda: self.sub_a_indexed_indirect('ix'), 'sub (ix + d)'),
            0x9e: Op(lambda: self.sbc_a_indexed_indirect('ix'), 'sbc (ix + d)'),

            0xa6: Op(lambda: self.and_indexed_indirect('ix'), 'and (ix + d)'),
            0xae: Op(lambda: self.xor_indexed_indirect('ix'), 'xor (ix + d)'),
            0xb6: Op(lambda: self.or_indexed_indirect('ix'), 'or (ix + d)'),
            0xbe: Op(lambda: self.cp_indexed_indirect('ix'), 'cp (ix + d)'),

            0xcb: self.init_indexed_cb_opcodes('ix'),

            0xe1: Op(lambda: self.pop_indexed('ix'), 'pop ix'),
            0xe3: Op(lambda: self.ex_sp_indirect_index_reg('ix'), 'ex (sp), ix'),
            0xe5: Op(lambda: self.push_indexed('ix'), 'push ix'),
            0xe9: Op(lambda: jp_indexed_indirect(self, 'ix'), 'jp (ix)'),

            0xf9: Op(lambda: self.ld_sp_indexed_16reg('ix'), 'ld sp, ix')
        }

    def init_fd_opcodes(self):
        return {
            0x09: Op(lambda: add_indexed_reg(self, 'iy', 'bc'), 'add iy, bc'),
            0x19: Op(lambda: add_indexed_reg(self, 'iy', 'de'), 'add iy, de'),
            0x21: Op(lambda: self.ld_indexed_reg_immediate('iy'), 'ld iy, nn'),
            0x22: Op(lambda: self.ld_ext_indexed_16reg('iy'), 'ld (nn), iy'),
            0x23: Op(lambda: inc_indexed_reg(self, 'iy'), 'inc iy'),
            0x29: Op(lambda: add_indexed_reg(self, 'iy', 'iy'), 'add iy, iy'),
            0x2a: Op(lambda: self.ld_indexed_16reg_ext('iy'), 'ld iy, (nn)'),
            0x2b: Op(lambda: dec_indexed_reg(self, 'iy'), 'dec iy'),
            0x34: Op(lambda: self.inc_indexed_indirect('iy'), 'inc (iy + d)'),
            0x35: Op(lambda: self.dec_indexed_indirect('iy'), 'dec (iy + d)'),
            0x36: Op(lambda: self.ld_indexed_addr_immediate('iy'), 'ld (iy + d), n'),
            0x39: Op(lambda: add_indexed_reg(self, 'iy', 'sp'), 'add iy, sp'),
            0x46: Op(lambda: self.ld_reg_indexed_addr('b', 'iy'), 'ld b, (iy + d)'),
            0x4e: Op(lambda: self.ld_reg_indexed_addr('c', 'iy'), 'ld c, (iy + d)'),
            0x56: Op(lambda: self.ld_reg_indexed_addr('d', 'iy'), 'ld d, (iy + d)'),
            0x5e: Op(lambda: self.ld_reg_indexed_addr('e', 'iy'), 'ld e, (iy + d)'),
            0x66: Op(lambda: self.ld_reg_indexed_addr('h', 'iy'), 'ld h, (iy + d)'),
            0x6e: Op(lambda: self.ld_reg_indexed_addr('l', 'iy'), 'ld l, (iy + d)'),
            0x70: Op(lambda: self.ld_indexed_reg_from_reg('iy', 'b'), 'ld (iy + d), b'),
            0x71: Op(lambda: self.ld_indexed_reg_from_reg('iy', 'c'), 'ld (iy + d), c'),
            0x72: Op(lambda: self.ld_indexed_reg_from_reg('iy', 'd'), 'ld (iy + d), d'),
            0x73: Op(lambda: self.ld_indexed_reg_from_reg('iy', 'e'), 'ld (iy + d), e'),
            0x74: Op(lambda: self.ld_indexed_reg_from_reg('iy', 'h'), 'ld (iy + d), h'),
            0x75: Op(lambda: self.ld_indexed_reg_from_reg('iy', 'l'), 'ld (iy + d), l'),
            0x77: Op(lambda: self.ld_indexed_reg_from_reg('iy', 'a'), 'ld (iy + d), a'),
            0x7e: Op(lambda: self.ld_reg_indexed_addr('a', 'iy'), 'ld a, (iy + d)'),

            0x86: Op(lambda: self.add_a_indexed_indirect('iy'), 'add a, (iy + d)'),
            0x8e: Op(lambda: self.adc_a_indexed_indirect('iy'), 'adc a, (iy + d)'),

            0x96: Op(lambda: self.sub_a_indexed_indirect('iy'), 'sub (iy + d)'),
            0x9e: Op(lambda: self.sbc_a_indexed_indirect('iy'), 'sbc (iy + d)'),

            0xa6: Op(lambda: self.and_indexed_indirect('iy'), 'and (ix + y)'),
            0xae: Op(lambda: self.xor_indexed_indirect('iy'), 'xor (iy + d)'),
            0xb6: Op(lambda: self.or_indexed_indirect('iy'), 'or (iy + d)'),
            0xbe: Op(lambda: self.cp_indexed_indirect('iy'), 'cp (iy + d)'),

            0xcb: self.init_indexed_cb_opcodes('iy'),

            0xe1: Op(lambda: self.pop_indexed('iy'), 'pop iy'),
            0xe3: Op(lambda: self.ex_sp_indirect_index_reg('iy'), 'ex (sp), iy'),
            0xe5: Op(lambda: self.push_indexed('iy'), 'push iy'),
            0xe9: Op(lambda: jp_indexed_indirect(self, 'iy'), 'jp (iy)'),

            0xf9: Op(lambda: self.ld_sp_indexed_16reg('iy'), 'ld sp, iy')
        }

    def init_indexed_cb_opcodes(self, reg):
        return {
            0x06: lambda offset: Op(lambda: rlc_indexed(self, self.memory, reg, offset), 'rlc ({} + d)'.format(reg)),
            0x0e: lambda offset: Op(lambda: rrc_indexed(self, self.memory, reg, offset), 'rrc ({} + d)'.format(reg)),
            0x16: lambda offset: Op(lambda: rl_indexed(self, self.memory, reg, offset), 'rl ({} + d)'.format(reg)),
            0x1e: lambda offset: Op(lambda: rr_indexed(self, self.memory, reg, offset), 'rr ({} + d)'.format(reg)),
            0x26: lambda offset: Op(lambda: sla_indexed(self, self.memory, reg, offset), 'sla ({} + d)'.format(reg)),
            0x2e: lambda offset: Op(lambda: sra_indexed(self, self.memory, reg, offset), 'sra ({} + d)'.format(reg)),
            0x3e: lambda offset: Op(lambda: srl_indexed(self, self.memory, reg, offset), 'srl ({} + d)'.format(reg)),

            0x46: lambda offset: Op(lambda: bit_indexed_indirect(self, self.memory, reg, offset, 0), 'bit 0, ({} + d)'.format(reg)),
            0x4e: lambda offset: Op(lambda: bit_indexed_indirect(self, self.memory, reg, offset, 1), 'bit 1, ({} + d)'.format(reg)),
            0x56: lambda offset: Op(lambda: bit_indexed_indirect(self, self.memory, reg, offset, 2), 'bit 2, ({} + d)'.format(reg)),
            0x5e: lambda offset: Op(lambda: bit_indexed_indirect(self, self.memory, reg, offset, 3), 'bit 3, ({} + d)'.format(reg)),
            0x66: lambda offset: Op(lambda: bit_indexed_indirect(self, self.memory, reg, offset, 4), 'bit 4, ({} + d)'.format(reg)),
            0x6e: lambda offset: Op(lambda: bit_indexed_indirect(self, self.memory, reg, offset, 5), 'bit 5, ({} + d)'.format(reg)),
            0x76: lambda offset: Op(lambda: bit_indexed_indirect(self, self.memory, reg, offset, 6), 'bit 6, ({} + d)'.format(reg)),
            0x7e: lambda offset: Op(lambda: bit_indexed_indirect(self, self.memory, reg, offset, 7), 'bit 7, ({} + d)'.format(reg)),

            0x86: lambda offset: Op(lambda: res_indexed_indirect(self, self.memory, reg, offset, 0), 'res 0, ({} + d)'.format(reg)),
            0x8e: lambda offset: Op(lambda: res_indexed_indirect(self, self.memory, reg, offset, 1), 'res 1, ({} + d)'.format(reg)),
            0x96: lambda offset: Op(lambda: res_indexed_indirect(self, self.memory, reg, offset, 2), 'res 2, ({} + d)'.format(reg)),
            0x9e: lambda offset: Op(lambda: res_indexed_indirect(self, self.memory, reg, offset, 3), 'res 3, ({} + d)'.format(reg)),
            0xa6: lambda offset: Op(lambda: res_indexed_indirect(self, self.memory, reg, offset, 4), 'res 4, ({} + d)'.format(reg)),
            0xae: lambda offset: Op(lambda: res_indexed_indirect(self, self.memory, reg, offset, 5), 'res 5, ({} + d)'.format(reg)),
            0xb6: lambda offset: Op(lambda: res_indexed_indirect(self, self.memory, reg, offset, 6), 'res 6, ({} + d)'.format(reg)),
            0xbe: lambda offset: Op(lambda: res_indexed_indirect(self, self.memory, reg, offset, 7), 'res 7, ({} + d)'.format(reg)),

            0xc6: lambda offset: Op(lambda: set_indexed_indirect(self, self.memory, reg, offset, 0), 'set 0, ({} + d)'.format(reg)),
            0xce: lambda offset: Op(lambda: set_indexed_indirect(self, self.memory, reg, offset, 1), 'set 1, ({} + d)'.format(reg)),
            0xd6: lambda offset: Op(lambda: set_indexed_indirect(self, self.memory, reg, offset, 2), 'set 2, ({} + d)'.format(reg)),
            0xde: lambda offset: Op(lambda: set_indexed_indirect(self, self.memory, reg, offset, 3), 'set 3, ({} + d)'.format(reg)),
            0xe6: lambda offset: Op(lambda: set_indexed_indirect(self, self.memory, reg, offset, 4), 'set 4, ({} + d)'.format(reg)),
            0xee: lambda offset: Op(lambda: set_indexed_indirect(self, self.memory, reg, offset, 5), 'set 5, ({} + d)'.format(reg)),
            0xf6: lambda offset: Op(lambda: set_indexed_indirect(self, self.memory, reg, offset, 6), 'set 6, ({} + d)'.format(reg)),
            0xfe: lambda offset: Op(lambda: set_indexed_indirect(self, self.memory, reg, offset, 7), 'set 7, ({} + d)'.format(reg))
        }

    def ei(self):
        self.enable_iff = True

    def set_iff(self):
        self.iff[0] = True
        self.iff[1] = True

    def di(self):
        self.iff[0] = False
        self.iff[1] = False

    def nmi(self):
        self.halting = False
        self.iff[0] = False
        self.push_pc()
        self.special_registers['pc'] = 0x0066

    def reti(self):
        ret(self)

    def retn(self):
        self.iff[0] = self.iff[1]
        ret(self)

    def halt(self):
        self.halting = True

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
        if not isinstance(operation, Op):
            operation.execute()
        else:
            operation.function()
        if enable_iff_after_op:
            self.set_iff()
            self.enable_iff = False
        self.cycles += 1
        return operation

    def get_operation(self):
        if self.iff[0] and len(self.interrupt_requests) > 0:
            self.halting = False
            self.push_pc()
            next_request = self.interrupt_requests.pop(0)
            next_request.acknowledge()
            if self.interrupt_mode == 0:
                self.interrupt_data_queue = next_request.get_im0_data()
            elif self.interrupt_mode == 1:
                return Op(lambda: rst(self, 0x0038), 'im1 response')
            elif self.interrupt_mode == 2:
                table_index = big_endian_value([self.special_registers['r'] & 0xfe, self.special_registers['i']])
                jump_low_byte = self.memory.peek(table_index)
                jump_high_byte = self.memory.peek(table_index + 1)
                return Op(lambda: call_to(self, big_endian_value([jump_low_byte, jump_high_byte])), 'im2 response')

        if self.halting:
            op_code = 0x00
        else:
            op_code = self.get_next_byte()

        operation = self.operations_by_opcode[op_code]
        if isinstance(operation, dict):
            op_code = self.get_next_byte()
            operation = operation[op_code]
            if isinstance(operation, dict):
                offset = to_signed(self.get_next_byte())
                op_code = self.get_next_byte()
                operation = operation[op_code](offset)

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

    def increment(self, register_name):
        self.special_registers[register_name] += 1

    def ld_reg_from_reg_indirect(self, destination, source_register):
        address = self.get_16bit_reg(source_register)
        self.main_registers[destination] = self.memory.peek(address)

    def ld_reg_indirect_from_reg(self, destination_register, source_register):
        address = self.get_16bit_reg(destination_register)
        self.memory.poke(address, self.main_registers[source_register])

    def ld_a_i(self):
        self.main_registers['a'] = self.special_registers['i']

    def ld_reg_immediate(self, destination_register):
        operand = self.get_next_byte()
        self.main_registers[destination_register] = operand

    def ld_reg_indexed_addr(self, destination_register, index_register):
        operand = self.get_next_byte()
        offset = to_signed(operand)
        self.main_registers[destination_register] = self.memory.peek(self.index_registers[index_register] + offset)

    def ld_indexed_reg_from_reg(self, destination_index_register, source_register):
        operand = self.get_next_byte()
        offset = to_signed(operand)
        self.memory.poke(self.index_registers[destination_index_register] + offset,
                         self.main_registers[source_register])

    def ld_indexed_addr_immediate(self, index_register):
        operand = self.get_next_byte()
        immediate_value = self.get_next_byte()

        offset = to_signed(operand)
        self.memory.poke(self.index_registers[index_register] + offset, immediate_value)

    def ld_16reg_immediate(self, register_pair):
        lsb = self.get_next_byte()
        msb = self.get_next_byte()
        self.main_registers[register_pair[0]] = msb
        self.main_registers[register_pair[1]] = lsb

    def ld_sp_indexed_16reg(self, source_register_pair):
        self.special_registers['sp'] = self.index_registers[source_register_pair]

    def ld_indexed_reg_immediate(self, index_register):
        little_endian_address = self.get_address_at_pc()
        self.index_registers[index_register] = big_endian_value(little_endian_address)

    def ld_ext_indexed_16reg(self, source_register_pair):
        dest_address = big_endian_value(self.get_address_at_pc())
        high_byte, low_byte = high_low_pair(self.index_registers[source_register_pair])
        self.memory.poke(dest_address, low_byte)
        self.memory.poke(dest_address + 1, high_byte)

    def ld_ext_sp(self):
        dest_address = big_endian_value(self.get_address_at_pc())
        high_byte, low_byte = high_low_pair(self.special_registers['sp'])
        self.memory.poke(dest_address, low_byte)
        self.memory.poke(dest_address + 1, high_byte)

    def ld_ext_16reg(self, source_register_pair):
        dest_address = big_endian_value(self.get_address_at_pc())
        self.memory.poke(dest_address, self.main_registers[source_register_pair[1]])
        self.memory.poke(dest_address + 1, self.main_registers[source_register_pair[0]])

    def ld_indexed_16reg_ext(self, dest_register_pair):
        src_address = big_endian_value(self.get_address_at_pc())
        low_byte = self.memory.peek(src_address)
        high_byte = self.memory.peek(src_address + 1)
        self.index_registers[dest_register_pair] = big_endian_value([low_byte, high_byte])

    def ld_sp_ext(self):
        src_address = big_endian_value(self.get_address_at_pc())
        low_byte = self.memory.peek(src_address)
        high_byte = self.memory.peek(src_address + 1)
        self.special_registers['sp'] = big_endian_value([low_byte, high_byte])

    def push_indexed(self, register_pair):
        high_byte, low_byte = high_low_pair(self.index_registers[register_pair])
        self.push_byte(high_byte)
        self.push_byte(low_byte)

    def push_byte(self, byte):
        if self.special_registers['sp'] == 0:
            self.special_registers['sp'] = 0xffff
        else:
            self.special_registers['sp'] -= 1
        self.memory.poke(self.special_registers['sp'], byte)

    def pop_indexed(self, register_pair):
        lsb = self.pop_byte()
        msb = self.pop_byte()
        self.index_registers[register_pair] = big_endian_value([lsb, msb])

    def pop_byte(self):
        byte = self.memory.peek(self.special_registers['sp'])
        if self.special_registers['sp'] == 0xffff:
            self.special_registers['sp'] = 0
        else:
            self.special_registers['sp'] += 1
        return byte

    def ex_af_alt_af(self):
        self.ex_with_alternate('af')

    def ex_with_alternate(self, register_pair):
        old_main = [self.main_registers[register_pair[0]], self.main_registers[register_pair[1]]]
        self.main_registers[register_pair[0]] = self.alternate_registers[register_pair[0]]
        self.main_registers[register_pair[1]] = self.alternate_registers[register_pair[1]]
        self.alternate_registers[register_pair[0]] = old_main[0]
        self.alternate_registers[register_pair[1]] = old_main[1]

    def ex_sp_indirect_index_reg(self, register):
        old_index = self.index_registers[register]
        self.index_registers[register] = big_endian_value([self.memory.peek(self.special_registers['sp']),
                                                           self.memory.peek(self.special_registers['sp'] + 1)])

        high_byte, low_byte = high_low_pair(old_index)
        self.memory.poke(self.special_registers['sp'], low_byte)
        self.memory.poke(self.special_registers['sp'] + 1, high_byte)

    def block_transfer(self, increment):
        src_addr = self.get_16bit_reg('hl')
        tgt_addr = self.get_16bit_reg('de')

        self.memory.poke(tgt_addr, self.memory.peek(src_addr))

        src_addr = (src_addr + increment) % 0x10000
        self.set_16bit_reg('hl', src_addr)

        tgt_addr = (tgt_addr + increment) % 0x10000
        self.set_16bit_reg('de', tgt_addr)

        counter = self.decrement_bc()

        self.set_condition('h', False)
        self.set_condition('p', counter != 0)
        self.set_condition('n', False)

    def decrement_bc(self):
        counter = self.get_16bit_reg('bc')
        counter = (counter - 1) % 0x10000

        self.set_16bit_reg('bc', counter)
        return counter

    def ldi(self):
        self.block_transfer(1)

    def ldd(self):
        self.block_transfer(-1)

    def ldir(self):
        self.ldi()
        self.set_condition('p', False)
        if not (self.main_registers['b'] == 0x00 and self.main_registers['c'] == 0x00):
            self.special_registers['pc'] = (self.special_registers['pc'] - 2) % 0x10000

    def lddr(self):
        self.ldd()
        self.set_condition('p', False)
        if not (self.main_registers['b'] == 0x00 and self.main_registers['c'] == 0x00):
            self.special_registers['pc'] = (self.special_registers['pc'] - 2) % 0x10000

    def block_compare(self, increment):
        src_addr = self.get_16bit_reg('hl')

        value_to_compare = self.memory.peek(src_addr)
        result, half_carry, full_carry = bitwise_sub(self.main_registers['a'], value_to_compare)

        src_addr = (src_addr + increment) % 0x10000
        self.set_16bit_reg('hl', src_addr)

        new_bc = self.decrement_bc()

        self.set_condition('s', result & 0b10000000 != 0)
        self.set_condition('z', result == 0)
        self.set_condition('h', half_carry)
        self.set_condition('p', new_bc != 0)
        self.set_condition('n', True)

    def cpi(self):
        self.block_compare(1)

    def cpd(self):
        self.block_compare(-1)

    def cpir(self):
        self.cpi()
        if not (self.get_16bit_reg('bc') == 0x0000):
            self.special_registers['pc'] = (self.special_registers['pc'] - 2) % 0x10000

    def cpdr(self):
        self.cpd()
        if not (self.get_16bit_reg('bc') == 0x0000):
            self.special_registers['pc'] = (self.special_registers['pc'] - 2) % 0x10000

    def add_a_indexed_indirect(self, index_reg):
        offset = to_signed(self.get_next_byte())
        value = self.memory.peek(self.index_registers[index_reg] + offset)
        self.add_a(value, False)

    def adc_a_indexed_indirect(self, index_reg):
        offset = to_signed(self.get_next_byte())
        value = self.memory.peek(self.index_registers[index_reg] + offset)
        self.add_a(value, self.condition('c'))

    def sub_a_indexed_indirect(self, index_reg):
        offset = to_signed(self.get_next_byte())
        value = self.memory.peek(self.index_registers[index_reg] + offset)
        self.sub_a(value, False)

    def sbc_a_indexed_indirect(self, index_reg):
        offset = to_signed(self.get_next_byte())
        value = self.memory.peek(self.index_registers[index_reg] + offset)
        self.sub_a(value, self.condition('c'))

    def and_indexed_indirect(self, register):
        offset = to_signed(self.get_next_byte())
        self.and_a_value(self.memory.peek(self.index_registers[register] + offset))

    def and_a_value(self, value):
        result = self.main_registers['a'] & value
        self.main_registers['a'] = result
        self.set_condition('s', result & 0b10000000 > 0)
        self.set_condition('z', result == 0)
        self.set_condition('h', True)
        self.set_condition('p', has_parity(result))
        self.set_condition('n', False)
        self.set_condition('c', False)

    def or_a_immediate(self):
        self.or_a_value(self.get_next_byte())

    def or_hl_indirect(self):
        self.or_a_value(self.memory.peek(self.get_16bit_reg('hl')))

    def or_indexed_indirect(self, register):
        offset = to_signed(self.get_next_byte())
        self.or_a_value(self.memory.peek(self.index_registers[register] + offset))

    def xor_indexed_indirect(self, register):
        offset = to_signed(self.get_next_byte())
        self.xor_a_value(self.memory.peek(self.index_registers[register] + offset))

    def cp_reg(self, other_reg):
        self.cp(self.main_registers[other_reg], False)

    def cp_immediate(self):
        value = self.get_next_byte()
        self.cp(value, False)

    def cp_indexed_indirect(self, index_reg):
        offset = to_signed(self.get_next_byte())
        value = self.memory.peek(self.index_registers[index_reg] + offset)
        self.cp(value, False)

    def inc_reg(self, reg):
        self.main_registers[reg] = self.inc_value(self.main_registers[reg])

    def inc_indexed_indirect(self, register):
        offset = to_signed(self.get_next_byte())
        address = self.index_registers[register] + offset
        result = self.inc_value(self.memory.peek(address))
        self.memory.poke(address, result)

    def inc_value(self, value):
        self.set_condition('p', value == 0x7f)
        result, half_carry, _ = bitwise_add(value, 1)

        self.set_condition('s', to_signed(result) < 0)
        self.set_condition('z', result == 0)
        self.set_condition('h', half_carry)
        self.set_condition('n', False)
        return result

    def dec_reg(self, reg):
        self.main_registers[reg] = self.dec_value(self.main_registers[reg])

    def dec_indexed_indirect(self, register):
        offset = to_signed(self.get_next_byte())
        address = self.index_registers[register] + offset
        result = self.dec_value(self.memory.peek(address))
        self.memory.poke(address, result)

    def dec_value(self, value):
        self.set_condition('p', value == 0x80)
        result, half_carry, _ = bitwise_sub(value, 1)

        self.set_condition('s', to_signed(result) < 0)
        self.set_condition('z', result == 0)
        self.set_condition('h', half_carry)
        self.set_condition('n', True)
        return result

    def neg(self):
        result, half_carry, _ = bitwise_sub(0, self.main_registers['a'])

        self.set_condition('s', to_signed(result) < 0)
        self.set_condition('z', result == 0)
        self.set_condition('h', half_carry)
        self.set_condition('p', self.main_registers['a'] == 0x80)
        self.set_condition('n', True)
        self.set_condition('c', self.main_registers['a'] != 0x00)
        self.main_registers['a'] = result

    def nop(self):
        pass

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