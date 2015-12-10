from funcs import *
from rotate_shift import *

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

    def create_ld_reg_from_reg(self, destination, source):
        return Op(lambda: self.ld_reg_from_reg(destination, source), 'ld {}, {}'.format(destination, source))

    def create_ld_reg_from_reg_indirect(self, destination, source_register):
        return Op(lambda: self.ld_reg_from_reg_indirect(destination, source_register),
                  'ld {}, ({})'.format(destination, source_register))

    def create_ld_reg_indirect_from_reg(self, destination_register, source_register):
        return Op(lambda: self.ld_reg_indirect_from_reg(destination_register, source_register),
                  'ld ({}), {}'.format(destination_register, source_register))

    def init_opcode_map(self):
        return {
            0x00: Op(self.nop, 'nop'),

            0x01: Op(lambda: self.ld_16reg_immediate('bc'), 'ld bc, nn'),
            0x02: self.create_ld_reg_indirect_from_reg('bc', 'a'),
            0x03: Op(lambda: self.inc_16reg('bc'), 'inc bc'),
            0x04: Op(lambda: self.inc_reg('b'), 'inc b'),
            0x05: Op(lambda: self.dec_reg('b'), 'dec b'),
            0x06: Op(lambda: self.ld_reg_immediate('b'), 'ld b, n'),
            0x07: Op(lambda: rlca(self), 'rlca'),
            0x08: Op(self.ex_af_alt_af, "ex af, af'"),
            0x09: Op(lambda: self.add_hl_reg('bc'), 'add hl, bc'),
            0x0a: self.create_ld_reg_from_reg_indirect('a', 'bc'),
            0x0b: Op(lambda: self.dec_16reg('bc'), 'dec bc'),
            0x0c: Op(lambda: self.inc_reg('c'), 'inc c'),
            0x0d: Op(lambda: self.dec_reg('c'), 'dec c'),
            0x0e: Op(lambda: self.ld_reg_immediate('c'), 'ld c, n'),
            0x0f: Op(lambda: rrca(self), 'rrca'),

            0x11: Op(lambda: self.ld_16reg_immediate('de'), 'ld de, nn'),
            0x12: self.create_ld_reg_indirect_from_reg('de', 'a'),
            0x13: Op(lambda: self.inc_16reg('de'), 'inc de'),
            0x14: Op(lambda: self.inc_reg('d'), 'inc d'),
            0x15: Op(lambda: self.dec_reg('d'), 'dec d'),
            0x16: Op(lambda: self.ld_reg_immediate('d'), 'ld d, n'),
            0x17: Op(lambda: rla(self), 'rla'),
            0x19: Op(lambda: self.add_hl_reg('de'), 'add hl, de'),
            0x1a: self.create_ld_reg_from_reg_indirect('a', 'de'),
            0x1b: Op(lambda: self.dec_16reg('de'), 'dec de'),
            0x1c: Op(lambda: self.inc_reg('e'), 'inc e'),
            0x1d: Op(lambda: self.dec_reg('e'), 'dec e'),
            0x1e: Op(lambda: self.ld_reg_immediate('e'), 'ld e, n'),
            0x1f: Op(lambda: rra(self), 'rra'),

            0x21: Op(lambda: self.ld_16reg_immediate('hl'), 'ld hl, nn'),
            0x22: Op(lambda: self.ld_ext_16reg('hl'), 'ld (nn), hl'),
            0x23: Op(lambda: self.inc_16reg('hl'), 'inc hl'),
            0x24: Op(lambda: self.inc_reg('h'), 'inc h'),
            0x25: Op(lambda: self.dec_reg('h'), 'dec h'),
            0x26: Op(lambda: self.ld_reg_immediate('h'), 'ld h, n'),
            0x27: Op(self.daa, 'daa'),
            0x29: Op(lambda: self.add_hl_reg('hl'), 'add hl, hl'),
            0x2a: Op(lambda: self.ld_16reg_ext('hl'), 'ld hl, (nn)'),
            0x2b: Op(lambda: self.dec_16reg('hl'), 'dec hl'),
            0x2c: Op(lambda: self.inc_reg('l'), 'inc l'),
            0x2d: Op(lambda: self.dec_reg('l'), 'dec l'),
            0x2e: Op(lambda: self.ld_reg_immediate('l'), 'ld l, n'),
            0x2f: Op(self.cpl, 'cpl'),

            0x31: Op(lambda: self.ld_sp_immediate(), 'ld sp, nn'),
            0x32: Op(self.ld_ext_addr_a, 'ld (nn), a'),
            0x33: Op(lambda: self.inc_16reg('sp'), 'inc sp'),
            0x34: Op(self.inc_hl_indirect, 'inc (hl)'),
            0x35: Op(self.dec_hl_indirect, 'dec (hl)'),
            0x36: Op(lambda: self.ld_hl_indirect_immediate(), 'ld (hl), n'),
            0x37: Op(self.scf, 'scf'),
            0x39: Op(lambda: self.add_hl_reg('sp'), 'add hl, sp'),
            0x3a: Op(self.ld_a_ext_addr, 'ld a, (nn)'),
            0x3b: Op(lambda: self.dec_16reg('sp'), 'dec sp'),
            0x3c: Op(lambda: self.inc_reg('a'), 'inc a'),
            0x3d: Op(lambda: self.dec_reg('a'), 'dec a'),
            0x3e: Op(lambda: self.ld_reg_immediate('a'), 'ld a, n'),
            0x3f: Op(self.ccf, 'ccf'),

            0x40: self.create_ld_reg_from_reg('b', 'b'),
            0x41: self.create_ld_reg_from_reg('b', 'c'),
            0x42: self.create_ld_reg_from_reg('b', 'd'),
            0x43: self.create_ld_reg_from_reg('b', 'e'),
            0x44: self.create_ld_reg_from_reg('b', 'h'),
            0x45: self.create_ld_reg_from_reg('b', 'l'),
            0x46: self.create_ld_reg_from_reg_indirect('b', 'hl'),
            0x47: self.create_ld_reg_from_reg('b', 'a'),

            0x48: self.create_ld_reg_from_reg('c', 'b'),
            0x49: self.create_ld_reg_from_reg('c', 'c'),
            0x4a: self.create_ld_reg_from_reg('c', 'd'),
            0x4b: self.create_ld_reg_from_reg('c', 'e'),
            0x4c: self.create_ld_reg_from_reg('c', 'h'),
            0x4d: self.create_ld_reg_from_reg('c', 'l'),
            0x4e: self.create_ld_reg_from_reg_indirect('c', 'hl'),
            0x4f: self.create_ld_reg_from_reg('c', 'a'),

            0x50: self.create_ld_reg_from_reg('d', 'b'),
            0x51: self.create_ld_reg_from_reg('d', 'c'),
            0x52: self.create_ld_reg_from_reg('d', 'd'),
            0x53: self.create_ld_reg_from_reg('d', 'e'),
            0x54: self.create_ld_reg_from_reg('d', 'h'),
            0x55: self.create_ld_reg_from_reg('d', 'l'),
            0x56: self.create_ld_reg_from_reg_indirect('d', 'hl'),
            0x57: self.create_ld_reg_from_reg('d', 'a'),

            0x58: self.create_ld_reg_from_reg('e', 'b'),
            0x59: self.create_ld_reg_from_reg('e', 'c'),
            0x5a: self.create_ld_reg_from_reg('e', 'd'),
            0x5b: self.create_ld_reg_from_reg('e', 'e'),
            0x5c: self.create_ld_reg_from_reg('e', 'h'),
            0x5d: self.create_ld_reg_from_reg('e', 'l'),
            0x5e: self.create_ld_reg_from_reg_indirect('e', 'hl'),
            0x5f: self.create_ld_reg_from_reg('e', 'a'),

            0x60: self.create_ld_reg_from_reg('h', 'b'),
            0x61: self.create_ld_reg_from_reg('h', 'c'),
            0x62: self.create_ld_reg_from_reg('h', 'd'),
            0x63: self.create_ld_reg_from_reg('h', 'e'),
            0x64: self.create_ld_reg_from_reg('h', 'h'),
            0x65: self.create_ld_reg_from_reg('h', 'l'),
            0x66: self.create_ld_reg_from_reg_indirect('h', 'hl'),
            0x67: self.create_ld_reg_from_reg('h', 'a'),

            0x68: self.create_ld_reg_from_reg('l', 'b'),
            0x69: self.create_ld_reg_from_reg('l', 'c'),
            0x6a: self.create_ld_reg_from_reg('l', 'd'),
            0x6b: self.create_ld_reg_from_reg('l', 'e'),
            0x6c: self.create_ld_reg_from_reg('l', 'h'),
            0x6d: self.create_ld_reg_from_reg('l', 'l'),
            0x6e: self.create_ld_reg_from_reg_indirect('l', 'hl'),
            0x6f: self.create_ld_reg_from_reg('l', 'a'),

            0x70: self.create_ld_reg_indirect_from_reg('hl', 'b'),
            0x71: self.create_ld_reg_indirect_from_reg('hl', 'c'),
            0x72: self.create_ld_reg_indirect_from_reg('hl', 'd'),
            0x73: self.create_ld_reg_indirect_from_reg('hl', 'e'),
            0x74: self.create_ld_reg_indirect_from_reg('hl', 'h'),
            0x75: self.create_ld_reg_indirect_from_reg('hl', 'l'),
            0x77: self.create_ld_reg_indirect_from_reg('hl', 'a'),

            0x78: self.create_ld_reg_from_reg('a', 'b'),
            0x79: self.create_ld_reg_from_reg('a', 'c'),
            0x7a: self.create_ld_reg_from_reg('a', 'd'),
            0x7b: self.create_ld_reg_from_reg('a', 'e'),
            0x7c: self.create_ld_reg_from_reg('a', 'h'),
            0x7d: self.create_ld_reg_from_reg('a', 'l'),
            0x7e: self.create_ld_reg_from_reg_indirect('a', 'hl'),
            0x7f: self.create_ld_reg_from_reg('a', 'a'),

            0x80: Op(lambda: self.add_a_reg('b'), 'add a, b'),
            0x81: Op(lambda: self.add_a_reg('c'), 'add a, c'),
            0x82: Op(lambda: self.add_a_reg('d'), 'add a, d'),
            0x83: Op(lambda: self.add_a_reg('e'), 'add a, e'),
            0x84: Op(lambda: self.add_a_reg('h'), 'add a, h'),
            0x85: Op(lambda: self.add_a_reg('l'), 'add a, l'),
            0x86: Op(self.add_a_hl_indirect, 'add a, (hl)'),
            0x87: Op(lambda: self.add_a_reg('a'), 'add a, a'),
            0x88: Op(lambda: self.adc_a_reg('b'), 'adc a, b'),
            0x89: Op(lambda: self.adc_a_reg('c'), 'adc a, c'),
            0x8a: Op(lambda: self.adc_a_reg('d'), 'adc a, d'),
            0x8b: Op(lambda: self.adc_a_reg('e'), 'adc a, e'),
            0x8c: Op(lambda: self.adc_a_reg('h'), 'adc a, h'),
            0x8d: Op(lambda: self.adc_a_reg('l'), 'adc a, l'),
            0x8e: Op(self.adc_a_hl_indirect, 'adc a, (hl)'),
            0x8f: Op(lambda: self.adc_a_reg('a'), 'adc a, a'),

            0x90: Op(lambda: self.sub_a_reg('b'), 'sub b'),
            0x91: Op(lambda: self.sub_a_reg('c'), 'sub c'),
            0x92: Op(lambda: self.sub_a_reg('d'), 'sub d'),
            0x93: Op(lambda: self.sub_a_reg('e'), 'sub e'),
            0x94: Op(lambda: self.sub_a_reg('h'), 'sub h'),
            0x95: Op(lambda: self.sub_a_reg('l'), 'sub l'),
            0x96: Op(self.sub_a_hl_indirect, 'sub (hl)'),
            0x97: Op(lambda: self.sub_a_reg('a'), 'sub a'),

            0x98: Op(lambda: self.sbc_a_reg('b'), 'sbc b'),
            0x99: Op(lambda: self.sbc_a_reg('c'), 'sbc c'),
            0x9a: Op(lambda: self.sbc_a_reg('d'), 'sbc d'),
            0x9b: Op(lambda: self.sbc_a_reg('e'), 'sbc e'),
            0x9c: Op(lambda: self.sbc_a_reg('h'), 'sbc h'),
            0x9d: Op(lambda: self.sbc_a_reg('l'), 'sbc l'),
            0x9e: Op(self.sbc_a_hl_indirect, 'sbc (hl)'),
            0x9f: Op(lambda: self.sbc_a_reg('a'), 'sbc a'),

            0xa0: Op(lambda: self.and_a_reg('b'), 'and b'),
            0xa1: Op(lambda: self.and_a_reg('c'), 'and c'),
            0xa2: Op(lambda: self.and_a_reg('d'), 'and d'),
            0xa3: Op(lambda: self.and_a_reg('e'), 'and e'),
            0xa4: Op(lambda: self.and_a_reg('h'), 'and h'),
            0xa5: Op(lambda: self.and_a_reg('l'), 'and l'),
            0xa6: Op(self.and_hl_indirect, 'and (hl)'),
            0xa7: Op(lambda: self.and_a_reg('a'), 'and a'),

            0xa8: Op(lambda: self.xor_a_reg('b'), 'xor b'),
            0xa9: Op(lambda: self.xor_a_reg('c'), 'xor c'),
            0xaa: Op(lambda: self.xor_a_reg('d'), 'xor d'),
            0xab: Op(lambda: self.xor_a_reg('e'), 'xor e'),
            0xac: Op(lambda: self.xor_a_reg('h'), 'xor h'),
            0xad: Op(lambda: self.xor_a_reg('l'), 'xor l'),
            0xae: Op(self.xor_hl_indirect, 'xor (hl)'),
            0xaf: Op(lambda: self.xor_a_reg('a'), 'xor a'),

            0xb0: Op(lambda: self.or_a_reg('b'), 'or b'),
            0xb1: Op(lambda: self.or_a_reg('c'), 'or c'),
            0xb2: Op(lambda: self.or_a_reg('d'), 'or d'),
            0xb3: Op(lambda: self.or_a_reg('e'), 'or e'),
            0xb4: Op(lambda: self.or_a_reg('h'), 'or h'),
            0xb5: Op(lambda: self.or_a_reg('l'), 'or l'),
            0xb6: Op(self.or_hl_indirect, 'or (hl)'),
            0xb7: Op(lambda: self.or_a_reg('a'), 'or a'),

            0xb8: Op(lambda: self.cp_reg('b'), 'cp b'),
            0xb9: Op(lambda: self.cp_reg('c'), 'cp c'),
            0xba: Op(lambda: self.cp_reg('d'), 'cp d'),
            0xbb: Op(lambda: self.cp_reg('e'), 'cp e'),
            0xbc: Op(lambda: self.cp_reg('h'), 'cp h'),
            0xbd: Op(lambda: self.cp_reg('l'), 'cp l'),
            0xbe: Op(self.cp_hl_indirect, 'cp (hl)'),
            0xbf: Op(lambda: self.cp_reg('a'), 'cp a'),

            0xc1: Op(lambda: self.pop('bc'), 'pop bc'),
            0xc5: Op(lambda: self.push('bc'), 'push bc'),
            0xc6: Op(self.add_a_immediate, 'add a, n'),
            0xce: Op(self.adc_a_immediate, 'adc a, n'),

            0xd1: Op(lambda: self.pop('de'), 'pop de'),
            0xd5: Op(lambda: self.push('de'), 'push de'),
            0xd6: Op(self.sub_a_immediate, 'sub n'),
            0xd9: Op(self.exx, 'exx'),
            0xde: Op(self.sbc_a_immediate, 'sbc n'),

            0xe1: Op(lambda: self.pop('hl'), 'pop hl'),
            0xe5: Op(lambda: self.push('hl'), 'push hl'),
            0xe3: Op(self.ex_sp_indirect_hl, 'ex (sp), hl'),
            0xe6: Op(self.and_a_immediate, 'and a, n'),
            0xeb: Op(self.ex_de_hl, 'ex de, hl'),
            0xee: Op(self.xor_a_immediate, 'xor a, n'),

            0xf1: Op(lambda: self.pop('af'), 'pop af'),
            0xf5: Op(lambda: self.push('af'), 'push af'),
            0xf6: Op(self.or_a_immediate, 'or a, n'),
            0xf9: Op(self.ld_sp_hl, 'ld sp, hl'),
            0xfe: Op(self.cp_immediate, 'cp n'),

            0xcb: self.init_cb_opcodes(),
            0xed: self.init_ed_opcodes(),
            0xdd: self.init_dd_opcodes(),
            0xfd: self.init_fd_opcodes()
        }

    def init_cb_opcodes(self):
        return {
            0x00: Op(lambda: rlc_reg(self, 'b'), 'rlc b'),
            0x01: Op(lambda: rlc_reg(self, 'c'), 'rlc c'),
            0x02: Op(lambda: rlc_reg(self, 'd'), 'rlc d'),
            0x03: Op(lambda: rlc_reg(self, 'e'), 'rlc e'),
            0x04: Op(lambda: rlc_reg(self, 'h'), 'rlc h'),
            0x05: Op(lambda: rlc_reg(self, 'l'), 'rlc l'),
            0x07: Op(lambda: rlc_reg(self, 'a'), 'rlc a')
        }

    def init_ed_opcodes(self):
        return {
            0x42: Op(lambda: self.sbc_hl_reg('bc'), 'sbc hl, bc'),
            0x43: Op(lambda: self.ld_ext_16reg('bc'), 'ld (nn), bc'),
            0x44: Op(self.neg, 'neg'),
            0x4a: Op(lambda: self.adc_hl_reg('bc'), 'adc hl, bc'),
            0x4b: Op(lambda: self.ld_16reg_ext('bc'), 'ld bc, (nn)'),

            0x52: Op(lambda: self.sbc_hl_reg('de'), 'sbc hl, de'),
            0x53: Op(lambda: self.ld_ext_16reg('de'), 'ld (nn), de'),
            0x5a: Op(lambda: self.adc_hl_reg('de'), 'adc hl, de'),
            0x5b: Op(lambda: self.ld_16reg_ext('de'), 'ld de, (nn)'),

            0x62: Op(lambda: self.sbc_hl_reg('hl'), 'sbc hl, hl'),
            0x63: Op(lambda: self.ld_ext_16reg('hl'), 'ld (nn), hl'),
            0x6a: Op(lambda: self.adc_hl_reg('hl'), 'adc hl, hl'),
            0x6b: Op(lambda: self.ld_16reg_ext('hl'), 'ld hl, (nn)'),

            0x72: Op(lambda: self.sbc_hl_reg('sp'), 'sbc hl, sp'),
            0x73: Op(lambda: self.ld_ext_sp(), 'ld (nn), sp'),
            0x7a: Op(lambda: self.adc_hl_reg('sp'), 'adc hl, sp'),
            0x7b: Op(lambda: self.ld_sp_ext(), 'ld sp, (nn)'),

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
            0x09: Op(lambda: self.add_indexed_reg('ix', 'bc'), 'add ix, bc'),
            0x19: Op(lambda: self.add_indexed_reg('ix', 'de'), 'add ix, de'),
            0x21: Op(lambda: self.ld_indexed_reg_immediate('ix'), 'ld ix, nn'),
            0x22: Op(lambda: self.ld_ext_indexed_16reg('ix'), 'ld (nn), ix'),
            0x23: Op(lambda: self.inc_indexed_reg('ix'), 'inc ix'),
            0x29: Op(lambda: self.add_indexed_reg('ix', 'ix'), 'add ix, ix'),
            0x2a: Op(lambda: self.ld_indexed_16reg_ext('ix'), 'ld ix, (nn)'),
            0x2b: Op(lambda: self.dec_indexed_reg('ix'), 'dec ix'),
            0x34: Op(lambda: self.inc_indexed_indirect('ix'), 'inc (ix + d)'),
            0x35: Op(lambda: self.dec_indexed_indirect('ix'), 'dec (ix + d)'),
            0x36: Op(lambda: self.ld_indexed_addr_immediate('ix'), 'ld (ix + d), n'),
            0x39: Op(lambda: self.add_indexed_reg('ix', 'sp'), 'add ix, sp'),
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

            0xe1: Op(lambda: self.pop_indexed('ix'), 'pop ix'),
            0xe3: Op(lambda: self.ex_sp_indirect_index_reg('ix'), 'ex (sp), ix'),
            0xe5: Op(lambda: self.push_indexed('ix'), 'push ix'),

            0xf9: Op(lambda: self.ld_sp_indexed_16reg('ix'), 'ld sp, ix')
        }

    def init_fd_opcodes(self):
        return {
            0x09: Op(lambda: self.add_indexed_reg('iy', 'bc'), 'add iy, bc'),
            0x19: Op(lambda: self.add_indexed_reg('iy', 'de'), 'add iy, de'),
            0x21: Op(lambda: self.ld_indexed_reg_immediate('iy'), 'ld iy, nn'),
            0x22: Op(lambda: self.ld_ext_indexed_16reg('iy'), 'ld (nn), iy'),
            0x23: Op(lambda: self.inc_indexed_reg('iy'), 'inc iy'),
            0x29: Op(lambda: self.add_indexed_reg('iy', 'iy'), 'add iy, iy'),
            0x2a: Op(lambda: self.ld_indexed_16reg_ext('iy'), 'ld iy, (nn)'),
            0x2b: Op(lambda: self.dec_indexed_reg('iy'), 'dec iy'),
            0x34: Op(lambda: self.inc_indexed_indirect('iy'), 'inc (iy + d)'),
            0x35: Op(lambda: self.dec_indexed_indirect('iy'), 'dec (iy + d)'),
            0x36: Op(lambda: self.ld_indexed_addr_immediate('iy'), 'ld (iy + d), n'),
            0x39: Op(lambda: self.add_indexed_reg('iy', 'sp'), 'add iy, sp'),
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

            0xe1: Op(lambda: self.pop_indexed('iy'), 'pop iy'),
            0xe3: Op(lambda: self.ex_sp_indirect_index_reg('iy'), 'ex (sp), iy'),
            0xe5: Op(lambda: self.push_indexed('iy'), 'push iy'),

            0xf9: Op(lambda: self.ld_sp_indexed_16reg('iy'), 'ld sp, iy')
        }

    def execute(self):
        operation = self.get_operation()
        operation.function()
        self.cycles += 1

    def get_operation(self):
        op_code = self.get_value_at_pc()
        operation = self.operations_by_opcode[op_code]
        if isinstance(operation, dict):
            op_code = self.get_value_at_pc()
            operation = operation[op_code]
        return operation

    def get_address_at_pc(self):
        return [self.get_value_at_pc(), self.get_value_at_pc()]

    def get_value_at_pc(self):
        op_code = self.memory.peek(self.special_registers['pc'])
        self.increment('pc')
        return op_code

    def increment(self, register_name):
        self.special_registers[register_name] += 1

    def ld_reg_from_reg(self, destination, source):
        self.main_registers[destination] = self.main_registers[source]

    def ld_reg_from_reg_indirect(self, destination, source_register):
        address = self.get_16bit_reg(source_register)
        self.main_registers[destination] = self.memory.peek(address)

    def ld_reg_indirect_from_reg(self, destination_register, source_register):
        address = self.get_16bit_reg(destination_register)
        self.memory.poke(address, self.main_registers[source_register])

    def ld_a_i(self):
        self.main_registers['a'] = self.special_registers['i']

    def ld_reg_immediate(self, destination_register):
        operand = self.get_value_at_pc()
        self.main_registers[destination_register] = operand

    def ld_reg_indexed_addr(self, destination_register, index_register):
        operand = self.get_value_at_pc()
        offset = to_signed(operand)
        self.main_registers[destination_register] = self.memory.peek(self.index_registers[index_register] + offset)

    def ld_indexed_reg_from_reg(self, destination_index_register, source_register):
        operand = self.get_value_at_pc()
        offset = to_signed(operand)
        self.memory.poke(self.index_registers[destination_index_register] + offset,
                         self.main_registers[source_register])

    def ld_hl_indirect_immediate(self):
        operand = self.get_value_at_pc()
        self.memory.poke(self.get_16bit_reg('hl'), operand)

    def ld_a_ext_addr(self):
        little_endian_address = self.get_address_at_pc()
        self.main_registers['a'] = self.memory.peek(big_endian_value(little_endian_address))

    def ld_ext_addr_a(self):
        little_endian_address = self.get_address_at_pc()
        self.memory.poke(big_endian_value(little_endian_address), self.main_registers['a'])

    def ld_indexed_addr_immediate(self, index_register):
        operand = self.get_value_at_pc()
        immediate_value = self.get_value_at_pc()

        offset = to_signed(operand)
        self.memory.poke(self.index_registers[index_register] + offset, immediate_value)

    def ld_16reg_immediate(self, register_pair):
        lsb = self.get_value_at_pc()
        msb = self.get_value_at_pc()
        self.main_registers[register_pair[0]] = msb
        self.main_registers[register_pair[1]] = lsb

    def ld_sp_immediate(self):
        little_endian_address = self.get_address_at_pc()
        self.special_registers['sp'] = big_endian_value(little_endian_address)

    def ld_sp_indexed_16reg(self, source_register_pair):
        self.special_registers['sp'] = self.index_registers[source_register_pair]

    def ld_sp_hl(self):
        self.special_registers['sp'] = big_endian_value([self.main_registers['l'], self.main_registers['h']])

    def ld_indexed_reg_immediate(self, index_register):
        little_endian_address = self.get_address_at_pc()
        self.index_registers[index_register] = big_endian_value(little_endian_address)

    def ld_ext_indexed_16reg(self, source_register_pair):
        dest_address = big_endian_value(self.get_address_at_pc())
        self.memory.poke(dest_address, self.index_registers[source_register_pair] & 0xff)
        self.memory.poke(dest_address + 1, self.index_registers[source_register_pair] >> 8)

    def ld_ext_sp(self):
        dest_address = big_endian_value(self.get_address_at_pc())
        self.memory.poke(dest_address, self.special_registers['sp'] & 0xff)
        self.memory.poke(dest_address + 1, self.special_registers['sp'] >> 8)

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

    def ld_16reg_ext(self, dest_register_pair):
        src_address = big_endian_value(self.get_address_at_pc())
        low_byte = self.memory.peek(src_address)
        high_byte = self.memory.peek(src_address + 1)
        self.main_registers[dest_register_pair[0]] = high_byte
        self.main_registers[dest_register_pair[1]] = low_byte

    def push_indexed(self, register_pair):
        self.push_byte(self.index_registers[register_pair] >> 8)
        self.push_byte(self.index_registers[register_pair] & 0xff)

    def push(self, register_pair):
        self.push_byte(self.main_registers[register_pair[0]])
        self.push_byte(self.main_registers[register_pair[1]])

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

    def pop(self, register_pair):
        lsb = self.pop_byte()
        msb = self.pop_byte()
        self.main_registers[register_pair[0]] = msb
        self.main_registers[register_pair[1]] = lsb

    def pop_byte(self):
        byte = self.memory.peek(self.special_registers['sp'])
        if self.special_registers['sp'] == 0xffff:
            self.special_registers['sp'] = 0
        else:
            self.special_registers['sp'] += 1
        return byte

    def ex_de_hl(self):
        old_h = self.main_registers['h']
        old_l = self.main_registers['l']
        self.main_registers['h'] = self.main_registers['d']
        self.main_registers['l'] = self.main_registers['e']
        self.main_registers['d'] = old_h
        self.main_registers['e'] = old_l

    def ex_af_alt_af(self):
        self.ex_with_alternate('af')

    def exx(self):
        self.ex_with_alternate('bc')
        self.ex_with_alternate('de')
        self.ex_with_alternate('hl')

    def ex_sp_indirect_hl(self):
        old_h = self.main_registers['h']
        old_l = self.main_registers['l']

        self.main_registers['h'] = self.memory.peek(self.special_registers['sp'] + 1)
        self.main_registers['l'] = self.memory.peek(self.special_registers['sp'])

        self.memory.poke(self.special_registers['sp'], old_l)
        self.memory.poke(self.special_registers['sp'] + 1, old_h)

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
        self.memory.poke(self.special_registers['sp'], old_index & 0xff)
        self.memory.poke(self.special_registers['sp'] + 1, old_index >> 8)

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

    def add_a_reg(self, other_reg):
        self.add_a(self.main_registers[other_reg], False)

    def adc_a_reg(self, other_reg):
        self.add_a(self.main_registers[other_reg], self.condition('c'))

    def add_a_immediate(self):
        value = self.get_value_at_pc()
        self.add_a(value, False)

    def adc_a_immediate(self):
        value = self.get_value_at_pc()
        self.add_a(value, self.condition('c'))

    def add_a_hl_indirect(self):
        value = self.memory.peek(self.get_16bit_reg('hl'))
        self.add_a(value, False)

    def adc_a_hl_indirect(self):
        value = self.memory.peek(self.get_16bit_reg('hl'))
        self.add_a(value, self.condition('c'))

    def add_a_indexed_indirect(self, index_reg):
        offset = to_signed(self.get_value_at_pc())
        value = self.memory.peek(self.index_registers[index_reg] + offset)
        self.add_a(value, False)

    def adc_a_indexed_indirect(self, index_reg):
        offset = to_signed(self.get_value_at_pc())
        value = self.memory.peek(self.index_registers[index_reg] + offset)
        self.add_a(value, self.condition('c'))

    def add_a(self, value, carry):
        signed_a = to_signed(self.main_registers['a'])
        if carry:
            value = (value + 1) & 0xff
        result, half_carry, full_carry = bitwise_add(self.main_registers['a'], value)
        signed_result = to_signed(result)
        self.main_registers['a'] = result
        self.set_condition('s', signed_result < 0)
        self.set_condition('z', result == 0)
        self.set_condition('h', half_carry)
        self.set_condition('p', (signed_a < 0) != (signed_result < 0))
        self.set_condition('n', False)
        self.set_condition('c', full_carry)

    def sub_a_reg(self, other_reg):
        self.sub_a(self.main_registers[other_reg], False)

    def sbc_a_reg(self, other_reg):
        self.sub_a(self.main_registers[other_reg], self.condition('c'))

    def sub_a_immediate(self):
        value = self.get_value_at_pc()
        self.sub_a(value, False)

    def sbc_a_immediate(self):
        value = self.get_value_at_pc()
        self.sub_a(value, self.condition('c'))

    def sub_a_hl_indirect(self):
        value = self.memory.peek(self.get_16bit_reg('hl'))
        self.sub_a(value, False)

    def sbc_a_hl_indirect(self):
        value = self.memory.peek(self.get_16bit_reg('hl'))
        self.sub_a(value, self.condition('c'))

    def sub_a_indexed_indirect(self, index_reg):
        offset = to_signed(self.get_value_at_pc())
        value = self.memory.peek(self.index_registers[index_reg] + offset)
        self.sub_a(value, False)

    def sbc_a_indexed_indirect(self, index_reg):
        offset = to_signed(self.get_value_at_pc())
        value = self.memory.peek(self.index_registers[index_reg] + offset)
        self.sub_a(value, self.condition('c'))

    def sub_a(self, value, carry):
        signed_a = to_signed(self.main_registers['a'])
        if carry:
            value = (value + 1) & 0xff
        result, half_carry, full_carry = bitwise_sub(self.main_registers['a'], value)
        signed_result = to_signed(result)
        self.main_registers['a'] = result
        self.set_condition('s', signed_result < 0)
        self.set_condition('z', result == 0)
        self.set_condition('h', half_carry)
        self.set_condition('p', (signed_a < 0) != (signed_result < 0))
        self.set_condition('n', True)
        self.set_condition('c', full_carry)

    def and_a_reg(self, other_reg):
        self.and_a_value(self.main_registers[other_reg])

    def and_a_immediate(self):
        self.and_a_value(self.get_value_at_pc())

    def and_hl_indirect(self):
        self.and_a_value(self.memory.peek(self.get_16bit_reg('hl')))

    def and_indexed_indirect(self, register):
        offset = to_signed(self.get_value_at_pc())
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

    def or_a_reg(self, other_reg):
        self.or_a_value(self.main_registers[other_reg])

    def or_a_immediate(self):
        self.or_a_value(self.get_value_at_pc())

    def or_hl_indirect(self):
        self.or_a_value(self.memory.peek(self.get_16bit_reg('hl')))

    def or_indexed_indirect(self, register):
        offset = to_signed(self.get_value_at_pc())
        self.or_a_value(self.memory.peek(self.index_registers[register] + offset))

    def or_a_value(self, value):
        result = self.main_registers['a'] | value
        self.main_registers['a'] = result
        self.set_condition('s', result & 0b10000000 > 0)
        self.set_condition('z', result == 0)
        self.set_condition('h', False)
        self.set_condition('p', has_parity(result))
        self.set_condition('n', False)
        self.set_condition('c', False)

    def xor_a_reg(self, other_reg):
        self.xor_a_value(self.main_registers[other_reg])

    def xor_a_immediate(self):
        self.xor_a_value(self.get_value_at_pc())

    def xor_hl_indirect(self):
        self.xor_a_value(self.memory.peek(self.get_16bit_reg('hl')))

    def xor_indexed_indirect(self, register):
        offset = to_signed(self.get_value_at_pc())
        self.xor_a_value(self.memory.peek(self.index_registers[register] + offset))

    def xor_a_value(self, value):
        result = self.main_registers['a'] ^ value
        self.main_registers['a'] = result
        self.set_condition('s', result & 0b10000000 > 0)
        self.set_condition('z', result == 0)
        self.set_condition('h', False)
        self.set_condition('p', has_parity(result))
        self.set_condition('n', False)
        self.set_condition('c', False)

    def cp_reg(self, other_reg):
        self.cp(self.main_registers[other_reg], False)

    def cp_immediate(self):
        value = self.get_value_at_pc()
        self.cp(value, False)

    def cp_hl_indirect(self):
        value = self.memory.peek(self.get_16bit_reg('hl'))
        self.cp(value, False)

    def cp_indexed_indirect(self, index_reg):
        offset = to_signed(self.get_value_at_pc())
        value = self.memory.peek(self.index_registers[index_reg] + offset)
        self.cp(value, False)

    def cp(self, value, carry):
        signed_a = to_signed(self.main_registers['a'])
        if carry:
            value = (value + 1) & 0xff
        result, half_carry, full_carry = bitwise_sub(self.main_registers['a'], value)
        signed_result = to_signed(result)
        self.set_condition('s', signed_result < 0)
        self.set_condition('z', result == 0)
        self.set_condition('h', half_carry)
        self.set_condition('p', (signed_a < 0) != (signed_result < 0))
        self.set_condition('n', True)
        self.set_condition('c', full_carry)

    def inc_reg(self, reg):
        self.main_registers[reg] = self.inc_value(self.main_registers[reg])

    def inc_hl_indirect(self):
        address = self.get_16bit_reg('hl')
        result = self.inc_value(self.memory.peek(address))
        self.memory.poke(address, result)

    def inc_indexed_indirect(self, register):
        offset = to_signed(self.get_value_at_pc())
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

    def dec_hl_indirect(self):
        address = self.get_16bit_reg('hl')
        result = self.dec_value(self.memory.peek(address))
        self.memory.poke(address, result)

    def dec_indexed_indirect(self, register):
        offset = to_signed(self.get_value_at_pc())
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

    def daa(self):
        digits = [int(x,16) for x in hex(self.main_registers['a'])[2:].zfill(2)]
        fc = self.condition('c')
        hc = self.condition('h')

        if self.condition('n'):
            self.daa_after_sub(digits, fc, hc)
        else:
            self.daa_after_add(digits, fc, hc)

    def daa_after_add(self, digits, fc, hc):
        if not fc and not hc:
            if digits[0] <= 0x9 and digits[1] <= 0x9:
                pass
            elif digits[0] <= 0x8 and digits[1] >= 0xa:
                self.main_registers['a'] += 0x6
            elif digits[0] >= 0xa and digits[1] <= 0x9:
                self.main_registers['a'] += 0x60
                self.set_condition('c', True)
            elif digits[0] >= 0x9 and digits[1] >= 0xa:
                self.main_registers['a'] += 0x66
                self.set_condition('c', True)
        elif not fc and hc:
            if digits[0] <= 0x9 and digits[1] <= 0x3:
                self.main_registers['a'] += 0x6
            elif digits[0] >= 0xa and digits[1] <= 0x3:
                self.main_registers['a'] += 0x66
                self.set_condition('c', True)
        elif fc and not hc:
            if digits[0] <= 0x2 and digits[1] <= 0x9:
                self.main_registers['a'] += 0x60
                self.set_condition('c', True)
            elif digits[0] <= 0x2 and digits[1] >= 0xa:
                self.main_registers['a'] += 0x66
                self.set_condition('c', True)
        elif fc and hc:
            if digits[0] <= 0x3 and digits[1] <= 0x3:
                self.main_registers['a'] += 0x66
                self.set_condition('c', True)

        self.main_registers['a'] &= 0xff

        result = self.main_registers['a']
        self.set_condition('s', (result & 0b10000000) > 0)
        self.set_condition('z', result == 0)
        self.set_condition('p', has_parity(result))

    def daa_after_sub(self, digits, fc, hc):
        if not fc and not hc:
            if digits[0] <= 0x9 and digits[1] <= 0x9:
                pass
        elif not fc and hc:
            if digits[0] <= 0x8 and digits[1] >= 0x6:
                self.main_registers['a'] += 0xfa
        elif fc and not hc:
            if digits[0] >= 0x7 and digits[1] <= 0x9:
                self.main_registers['a'] += 0xa0
                self.set_condition('c', True)
        elif fc and hc:
            if digits[0] >= 0x6 and digits[1] >= 0x6:
                self.main_registers['a'] += 0x9a
                self.set_condition('c', True)

        self.main_registers['a'] &= 0xff

        result = self.main_registers['a']
        self.set_condition('s', (result & 0b10000000) > 0)
        self.set_condition('z', result == 0)
        self.set_condition('p', has_parity(result))

    def cpl(self):
        self.main_registers['a'] = 0xff - self.main_registers['a']
        self.set_condition('h', True)
        self.set_condition('n', True)

    def neg(self):
        result, half_carry, _ = bitwise_sub(0, self.main_registers['a'])

        self.set_condition('s', to_signed(result) < 0)
        self.set_condition('z', result == 0)
        self.set_condition('h', half_carry)
        self.set_condition('p', self.main_registers['a'] == 0x80)
        self.set_condition('n', True)
        self.set_condition('c', self.main_registers['a'] != 0x00)
        self.main_registers['a'] = result

    def ccf(self):
        self.set_condition('h', self.condition('c'))
        self.set_condition('c', not self.condition('c'))
        self.set_condition('n', False)

    def scf(self):
        self.set_condition('h', False)
        self.set_condition('n', False)
        self.set_condition('c', True)

    def nop(self):
        pass

    def add_hl_reg(self, reg_pair):
        result, half_carry, full_carry = bitwise_add_16bit(self.get_16bit_reg('hl'), self.get_16bit_reg(reg_pair))
        self.set_16bit_reg('hl', result)

        self.set_condition('h', half_carry)
        self.set_condition('n', False)
        self.set_condition('c', full_carry)

    def adc_hl_reg(self, reg_pair):
        signed_hl = to_signed_16bit(self.get_16bit_reg('hl'))
        to_add = (self.get_16bit_reg(reg_pair) + (1 if self.condition('c') else 0)) & 0xffff
        result, half_carry, full_carry = bitwise_add_16bit(self.get_16bit_reg('hl'), to_add)
        signed_result = to_signed_16bit(result)

        self.set_16bit_reg('hl', result)
        self.set_condition('s', result & 0x8000 > 0)
        self.set_condition('z', result == 0)
        self.set_condition('h', half_carry)
        self.set_condition('p', (signed_hl < 0) != (signed_result < 0))
        self.set_condition('n', False)
        self.set_condition('c', full_carry)

    def sbc_hl_reg(self, reg_pair):
        signed_hl = to_signed_16bit(self.get_16bit_reg('hl'))
        to_sub = (self.get_16bit_reg(reg_pair) + (1 if self.condition('c') else 0)) & 0xffff
        result, half_borrow, full_borrow = bitwise_sub_16bit(self.get_16bit_reg('hl'), to_sub)
        signed_result = to_signed_16bit(result)

        self.set_16bit_reg('hl', result)
        self.set_condition('s', result & 0x8000 > 0)
        self.set_condition('z', result == 0)
        self.set_condition('h', half_borrow)
        self.set_condition('p', (signed_hl < 0) != (signed_result < 0))
        self.set_condition('n', True)
        self.set_condition('c', full_borrow)

    def add_indexed_reg(self, indexed_reg, reg_pair):
        result, half_carry, full_carry = bitwise_add_16bit(self.index_registers[indexed_reg],
                                                           self.get_16bit_reg(reg_pair))

        self.index_registers[indexed_reg] = result
        self.set_condition('h', half_carry)
        self.set_condition('n', False)
        self.set_condition('c', full_carry)

    def inc_16reg(self, reg_pair):
        result = (self.get_16bit_reg(reg_pair) + 1) & 0xffff
        self.set_16bit_reg(reg_pair, result)

    def inc_indexed_reg(self, reg):
        result = (self.index_registers[reg] + 1) & 0xffff
        self.index_registers[reg] = result

    def dec_16reg(self, reg_pair):
        result = (self.get_16bit_reg(reg_pair) - 1) & 0xffff
        self.set_16bit_reg(reg_pair, result)

    def dec_indexed_reg(self, reg):
        result = (self.index_registers[reg] - 1) & 0xffff
        self.index_registers[reg] = result

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
            self.main_registers[register_pair[0]] = val_16bit >> 8
            self.main_registers[register_pair[1]] = val_16bit & 0xff

    def get_16bit_alt_reg(self, register_pair):
        msb = self.alternate_registers[register_pair[0]]
        lsb = self.alternate_registers[register_pair[1]]
        return big_endian_value([lsb, msb])
