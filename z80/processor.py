from arithmetic_16 import *
from baseop import *
from call import *
from exchange_operations import *
from inc_operations import *
from interrupt_operations import *
from jump import *
from ld_operations import *
from rotate import *
from stack import *
from z80.arithmetic_8 import *
from z80.block_operations import *
from z80.dd_fd_group import OpDdFdGroup
from z80.ed_group import OpEdGroup
from z80.io import *
from cb_group import OpCbGroup


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
        self.interrupt_data_exists = False
        self.interrupt_mode = 0
        self.interrupt_requests = []
        self.interrupt_requests_exist = False
        self.halting = False
        self.im1_response_op = OpRst(self, 0x0038, True)
        self.last_operation = None
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

            0xcb: OpCbGroup(self, self.memory),
            0xed: OpEdGroup(self, self.memory, self.io),
            0xdd: OpDdFdGroup('ix', self, self.memory),
            0xfd: OpDdFdGroup('iy', self, self.memory)
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
        self.interrupt_requests_exist = True

    def push_pc(self):
        high_byte, low_byte = high_low_pair(self.special_registers['pc'])
        self.push_byte(high_byte)
        self.push_byte(low_byte)

    def execute(self):
        enable_iff_after_op = self.enable_iff
        special_registers = self.special_registers

        before_pc = special_registers['pc']
        operation, interrupt_triggered, after_pc = self.get_operation(before_pc)

        t_states, jumped, after_pc = operation.execute(self, self.memory, after_pc)
        if enable_iff_after_op:
            self.set_iff()
            self.enable_iff = False
        self.last_operation = operation

        if not jumped:
            special_registers['pc'] = after_pc

        # increment refresh register
        if not interrupt_triggered:
            current_r = special_registers['r']
            high_bit = current_r & 0b10000000
            low_bits = current_r & 0b01111111
            low_bits += ((after_pc - before_pc) & 0xffff)
            special_registers['r'] = high_bit | (low_bits & 0b01111111)

        return t_states

    def get_operation(self, pc):
        if self.iff[0] and self.interrupt_requests_exist:
            interrupt_mode = self.interrupt_mode
            self.halting = False
            next_request = self.interrupt_requests.pop(0)
            if len(self.interrupt_requests) == 0:
                self.interrupt_requests_exist = False
            next_request.acknowledge()
            if interrupt_mode == 1:
                return self.im1_response_op, True, pc
            elif interrupt_mode == 2:
                table_index = big_endian_value([self.special_registers['r'] & 0xfe, self.special_registers['i']])
                jump_low_byte = self.memory[0xffff & table_index]
                jump_high_byte = self.memory[0xffff & (table_index + 1)]
                return OpCallDirect(self, big_endian_value([jump_low_byte, jump_high_byte]), True), True, pc

        if self.halting:
            op_code = 0x00
        else:
            op_code = self.memory[pc]

        return self.operations_by_opcode[op_code], False, (pc + 1) & 0xffff

    # def get_address_at_pc(self):
    #     return [self.get_next_byte(), self.get_next_byte()]

    # def fetch_bytes(self):
    #    pc = self.special_registers['pc']
    #    bytes = self.memory[pc:pc+6 if pc < 0xfffb else 0x10000]
    #    bytes.extend(self.memory[0:6 - len(bytes)])
    #    return bytes

    # def get_next_byte(self):
    #     if self.interrupt_data_exists:
    #         item = self.interrupt_data_queue.pop()
    #         if len(self.interrupt_data_queue) == 0:
    #             self.interrupt_data_exists = False
    #         return item
    #     else:
    #         # increment refresh register
    #         # current_r = self.special_registers['r']
    #         # high_bit = current_r & 0b10000000
    #         # low_bits = current_r & 0b01111111
    #         # low_bits += 1
    #         self.special_registers['r'] = high_bit | (low_bits & 0b01111111)
    #
    #         pc_value = self.special_registers['pc']
    #         op_code = self.memory[0xffff & pc_value]
    #         self.special_registers['pc'] = (pc_value + 1) & 0xffff
    #         return op_code

    def get_signed_offset_byte(self):
        return to_signed(self.memory[0xffff & (self.special_registers['pc'] - 2)])

    def restore_pc_from_stack(self):
        self.special_registers['pc'] = self._get_destination_from_stack()

    def _get_destination_from_stack(self):
        return big_endian_value([self.pop_byte(), self.pop_byte()])

    def push_byte(self, byte):
        self.special_registers['sp'] = (self.special_registers['sp'] - 1) & 0xffff
        self.memory[0xffff & self.special_registers['sp']] = byte

    def pop_byte(self):
        byte = self.memory[0xffff & self.special_registers['sp']]
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
        else:
            main_registers = self.main_registers
            msb = main_registers[register_pair[0]]
            lsb = main_registers[register_pair[1]]
            return big_endian_value([lsb, msb])

    def set_16bit_reg(self, register_pair, val_16bit):
        if register_pair == 'sp':
            self.special_registers['sp'] = val_16bit
        else:
            high_byte, low_byte = high_low_pair(val_16bit)
            main_registers = self.main_registers
            main_registers[register_pair[0]] = high_byte
            main_registers[register_pair[1]] = low_byte

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