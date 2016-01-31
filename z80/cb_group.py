from z80.bit import *
from z80.shift import *
from z80.rotate import *


class OpCbGroup(BaseOp):
    def __init__(self, processor, memory):
        BaseOp.__init__(self)
        self.last_t_states = None
        self.processor = processor
        self.ops = {
            0x00: OpRlcReg(processor, 'b'),
            0x01: OpRlcReg(processor, 'c'),
            0x02: OpRlcReg(processor, 'd'),
            0x03: OpRlcReg(processor, 'e'),
            0x04: OpRlcReg(processor, 'h'),
            0x05: OpRlcReg(processor, 'l'),
            0x06: OpRlcHlIndirect(processor, memory),
            0x07: OpRlcReg(processor, 'a'),
            0x08: OpRrcReg(processor, 'b'),
            0x09: OpRrcReg(processor, 'c'),
            0x0a: OpRrcReg(processor, 'd'),
            0x0b: OpRrcReg(processor, 'e'),
            0x0c: OpRrcReg(processor, 'h'),
            0x0d: OpRrcReg(processor, 'l'),
            0x0e: OpRrcHlIndirect(processor, memory),
            0x0f: OpRrcReg(processor, 'a'),

            0x10: OpRlReg(processor, 'b'),
            0x11: OpRlReg(processor, 'c'),
            0x12: OpRlReg(processor, 'd'),
            0x13: OpRlReg(processor, 'e'),
            0x14: OpRlReg(processor, 'h'),
            0x15: OpRlReg(processor, 'l'),
            0x16: OpRlHlIndirect(processor, memory),
            0x17: OpRlReg(processor, 'a'),
            0x18: OpRrReg(processor, 'b'),
            0x19: OpRrReg(processor, 'c'),
            0x1a: OpRrReg(processor, 'd'),
            0x1b: OpRrReg(processor, 'e'),
            0x1c: OpRrReg(processor, 'h'),
            0x1d: OpRrReg(processor, 'l'),
            0x1e: OpRrHlIndirect(processor, memory),
            0x1f: OpRrReg(processor, 'a'),

            0x20: OpSlaReg(processor, 'b'),
            0x21: OpSlaReg(processor, 'c'),
            0x22: OpSlaReg(processor, 'd'),
            0x23: OpSlaReg(processor, 'e'),
            0x24: OpSlaReg(processor, 'h'),
            0x25: OpSlaReg(processor, 'l'),
            0x26: OpSlaHlIndirect(processor, memory),
            0x27: OpSlaReg(processor, 'a'),
            0x28: OpSraReg(processor, 'b'),
            0x29: OpSraReg(processor, 'c'),
            0x2a: OpSraReg(processor, 'd'),
            0x2b: OpSraReg(processor, 'e'),
            0x2c: OpSraReg(processor, 'h'),
            0x2d: OpSraReg(processor, 'l'),
            0x2e: OpSraHlIndirect(processor, memory),
            0x2f: OpSraReg(processor, 'a'),

            0x30: OpSllReg(processor, 'b'),
            0x31: OpSllReg(processor, 'c'),
            0x32: OpSllReg(processor, 'd'),
            0x33: OpSllReg(processor, 'e'),
            0x34: OpSllReg(processor, 'h'),
            0x35: OpSllReg(processor, 'l'),
            0x36: OpSllHlIndirect(processor, memory),
            0x37: OpSllReg(processor, 'a'),
            0x38: OpSrlReg(processor, 'b'),
            0x39: OpSrlReg(processor, 'c'),
            0x3a: OpSrlReg(processor, 'd'),
            0x3b: OpSrlReg(processor, 'e'),
            0x3c: OpSrlReg(processor, 'h'),
            0x3d: OpSrlReg(processor, 'l'),
            0x3e: OpSrlHlIndirect(processor, memory),
            0x3f: OpSrlReg(processor, 'a'),

            0x40: OpBitReg(processor, 'b', 0),
            0x41: OpBitReg(processor, 'c', 0),
            0x42: OpBitReg(processor, 'd', 0),
            0x43: OpBitReg(processor, 'e', 0),
            0x44: OpBitReg(processor, 'h', 0),
            0x45: OpBitReg(processor, 'l', 0),
            0x46: OpBitHlIndirect(processor, memory, 0),
            0x47: OpBitReg(processor, 'a', 0),
            0x48: OpBitReg(processor, 'b', 1),
            0x49: OpBitReg(processor, 'c', 1),
            0x4a: OpBitReg(processor, 'd', 1),
            0x4b: OpBitReg(processor, 'e', 1),
            0x4c: OpBitReg(processor, 'h', 1),
            0x4d: OpBitReg(processor, 'l', 1),
            0x4e: OpBitHlIndirect(processor, memory, 1),
            0x4f: OpBitReg(processor, 'a', 1),

            0x50: OpBitReg(processor, 'b', 2),
            0x51: OpBitReg(processor, 'c', 2),
            0x52: OpBitReg(processor, 'd', 2),
            0x53: OpBitReg(processor, 'e', 2),
            0x54: OpBitReg(processor, 'h', 2),
            0x55: OpBitReg(processor, 'l', 2),
            0x56: OpBitHlIndirect(processor, memory, 2),
            0x57: OpBitReg(processor, 'a', 2),
            0x58: OpBitReg(processor, 'b', 3),
            0x59: OpBitReg(processor, 'c', 3),
            0x5a: OpBitReg(processor, 'd', 3),
            0x5b: OpBitReg(processor, 'e', 3),
            0x5c: OpBitReg(processor, 'h', 3),
            0x5d: OpBitReg(processor, 'l', 3),
            0x5e: OpBitHlIndirect(processor, memory, 3),
            0x5f: OpBitReg(processor, 'a', 3),

            0x60: OpBitReg(processor, 'b', 4),
            0x61: OpBitReg(processor, 'c', 4),
            0x62: OpBitReg(processor, 'd', 4),
            0x63: OpBitReg(processor, 'e', 4),
            0x64: OpBitReg(processor, 'h', 4),
            0x65: OpBitReg(processor, 'l', 4),
            0x66: OpBitHlIndirect(processor, memory, 4),
            0x67: OpBitReg(processor, 'a', 4),
            0x68: OpBitReg(processor, 'b', 5),
            0x69: OpBitReg(processor, 'c', 5),
            0x6a: OpBitReg(processor, 'd', 5),
            0x6b: OpBitReg(processor, 'e', 5),
            0x6c: OpBitReg(processor, 'h', 5),
            0x6d: OpBitReg(processor, 'l', 5),
            0x6e: OpBitHlIndirect(processor, memory, 5),
            0x6f: OpBitReg(processor, 'a', 5),

            0x70: OpBitReg(processor, 'b', 6),
            0x71: OpBitReg(processor, 'c', 6),
            0x72: OpBitReg(processor, 'd', 6),
            0x73: OpBitReg(processor, 'e', 6),
            0x74: OpBitReg(processor, 'h', 6),
            0x75: OpBitReg(processor, 'l', 6),
            0x76: OpBitHlIndirect(processor, memory, 6),
            0x77: OpBitReg(processor, 'a', 6),
            0x78: OpBitReg(processor, 'b', 7),
            0x79: OpBitReg(processor, 'c', 7),
            0x7a: OpBitReg(processor, 'd', 7),
            0x7b: OpBitReg(processor, 'e', 7),
            0x7c: OpBitReg(processor, 'h', 7),
            0x7d: OpBitReg(processor, 'l', 7),
            0x7e: OpBitHlIndirect(processor, memory, 7),
            0x7f: OpBitReg(processor, 'a', 7),

            0x80: OpResReg(processor, 'b', 0),
            0x81: OpResReg(processor, 'c', 0),
            0x82: OpResReg(processor, 'd', 0),
            0x83: OpResReg(processor, 'e', 0),
            0x84: OpResReg(processor, 'h', 0),
            0x85: OpResReg(processor, 'l', 0),
            0x86: OpResHlIndirect(processor, memory, 0),
            0x87: OpResReg(processor, 'a', 0),
            0x88: OpResReg(processor, 'b', 1),
            0x89: OpResReg(processor, 'c', 1),
            0x8a: OpResReg(processor, 'd', 1),
            0x8b: OpResReg(processor, 'e', 1),
            0x8c: OpResReg(processor, 'h', 1),
            0x8d: OpResReg(processor, 'l', 1),
            0x8e: OpResHlIndirect(processor, memory, 1),
            0x8f: OpResReg(processor, 'a', 1),

            0x90: OpResReg(processor, 'b', 2),
            0x91: OpResReg(processor, 'c', 2),
            0x92: OpResReg(processor, 'd', 2),
            0x93: OpResReg(processor, 'e', 2),
            0x94: OpResReg(processor, 'h', 2),
            0x95: OpResReg(processor, 'l', 2),
            0x96: OpResHlIndirect(processor, memory, 2),
            0x97: OpResReg(processor, 'a', 2),
            0x98: OpResReg(processor, 'b', 3),
            0x99: OpResReg(processor, 'c', 3),
            0x9a: OpResReg(processor, 'd', 3),
            0x9b: OpResReg(processor, 'e', 3),
            0x9c: OpResReg(processor, 'h', 3),
            0x9d: OpResReg(processor, 'l', 3),
            0x9e: OpResHlIndirect(processor, memory, 3),
            0x9f: OpResReg(processor, 'a', 3),

            0xa0: OpResReg(processor, 'b', 4),
            0xa1: OpResReg(processor, 'c', 4),
            0xa2: OpResReg(processor, 'd', 4),
            0xa3: OpResReg(processor, 'e', 4),
            0xa4: OpResReg(processor, 'h', 4),
            0xa5: OpResReg(processor, 'l', 4),
            0xa6: OpResHlIndirect(processor, memory, 4),
            0xa7: OpResReg(processor, 'a', 4),
            0xa8: OpResReg(processor, 'b', 5),
            0xa9: OpResReg(processor, 'c', 5),
            0xaa: OpResReg(processor, 'd', 5),
            0xab: OpResReg(processor, 'e', 5),
            0xac: OpResReg(processor, 'h', 5),
            0xad: OpResReg(processor, 'l', 5),
            0xae: OpResHlIndirect(processor, memory, 5),
            0xaf: OpResReg(processor, 'a', 5),

            0xb0: OpResReg(processor, 'b', 6),
            0xb1: OpResReg(processor, 'c', 6),
            0xb2: OpResReg(processor, 'd', 6),
            0xb3: OpResReg(processor, 'e', 6),
            0xb4: OpResReg(processor, 'h', 6),
            0xb5: OpResReg(processor, 'l', 6),
            0xb6: OpResHlIndirect(processor, memory, 6),
            0xb7: OpResReg(processor, 'a', 6),
            0xb8: OpResReg(processor, 'b', 7),
            0xb9: OpResReg(processor, 'c', 7),
            0xba: OpResReg(processor, 'd', 7),
            0xbb: OpResReg(processor, 'e', 7),
            0xbc: OpResReg(processor, 'h', 7),
            0xbd: OpResReg(processor, 'l', 7),
            0xbe: OpResHlIndirect(processor, memory, 7),
            0xbf: OpResReg(processor, 'a', 7),

            0xc0: OpSetReg(processor, 'b', 0),
            0xc1: OpSetReg(processor, 'c', 0),
            0xc2: OpSetReg(processor, 'd', 0),
            0xc3: OpSetReg(processor, 'e', 0),
            0xc4: OpSetReg(processor, 'h', 0),
            0xc5: OpSetReg(processor, 'l', 0),
            0xc6: OpSetHlIndirect(processor, memory, 0),
            0xc7: OpSetReg(processor, 'a', 0),
            0xc8: OpSetReg(processor, 'b', 1),
            0xc9: OpSetReg(processor, 'c', 1),
            0xca: OpSetReg(processor, 'd', 1),
            0xcb: OpSetReg(processor, 'e', 1),
            0xcc: OpSetReg(processor, 'h', 1),
            0xcd: OpSetReg(processor, 'l', 1),
            0xce: OpSetHlIndirect(processor, memory, 1),
            0xcf: OpSetReg(processor, 'a', 1),

            0xd0: OpSetReg(processor, 'b', 2),
            0xd1: OpSetReg(processor, 'c', 2),
            0xd2: OpSetReg(processor, 'd', 2),
            0xd3: OpSetReg(processor, 'e', 2),
            0xd4: OpSetReg(processor, 'h', 2),
            0xd5: OpSetReg(processor, 'l', 2),
            0xd6: OpSetHlIndirect(processor, memory, 2),
            0xd7: OpSetReg(processor, 'a', 2),
            0xd8: OpSetReg(processor, 'b', 3),
            0xd9: OpSetReg(processor, 'c', 3),
            0xda: OpSetReg(processor, 'd', 3),
            0xdb: OpSetReg(processor, 'e', 3),
            0xdc: OpSetReg(processor, 'h', 3),
            0xdd: OpSetReg(processor, 'l', 3),
            0xde: OpSetHlIndirect(processor, memory, 3),
            0xdf: OpSetReg(processor, 'a', 3),

            0xe0: OpSetReg(processor, 'b', 4),
            0xe1: OpSetReg(processor, 'c', 4),
            0xe2: OpSetReg(processor, 'd', 4),
            0xe3: OpSetReg(processor, 'e', 4),
            0xe4: OpSetReg(processor, 'h', 4),
            0xe5: OpSetReg(processor, 'l', 4),
            0xe6: OpSetHlIndirect(processor, memory, 4),
            0xe7: OpSetReg(processor, 'a', 4),
            0xe8: OpSetReg(processor, 'b', 5),
            0xe9: OpSetReg(processor, 'c', 5),
            0xea: OpSetReg(processor, 'd', 5),
            0xeb: OpSetReg(processor, 'e', 5),
            0xec: OpSetReg(processor, 'h', 5),
            0xed: OpSetReg(processor, 'l', 5),
            0xee: OpSetHlIndirect(processor, memory, 5),
            0xef: OpSetReg(processor, 'a', 5),

            0xf0: OpSetReg(processor, 'b', 6),
            0xf1: OpSetReg(processor, 'c', 6),
            0xf2: OpSetReg(processor, 'd', 6),
            0xf3: OpSetReg(processor, 'e', 6),
            0xf4: OpSetReg(processor, 'h', 6),
            0xf5: OpSetReg(processor, 'l', 6),
            0xf6: OpSetHlIndirect(processor, memory, 6),
            0xf7: OpSetReg(processor, 'a', 6),
            0xf8: OpSetReg(processor, 'b', 7),
            0xf9: OpSetReg(processor, 'c', 7),
            0xfa: OpSetReg(processor, 'd', 7),
            0xfb: OpSetReg(processor, 'e', 7),
            0xfc: OpSetReg(processor, 'h', 7),
            0xfd: OpSetReg(processor, 'l', 7),
            0xfe: OpSetHlIndirect(processor, memory, 7),
            0xff: OpSetReg(processor, 'a', 7)
        }

    def execute(self):
        op = self.ops[self.processor.get_next_byte()]
        return op.execute()

    def __str__(self):
        return 'CB GROUP'
