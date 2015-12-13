from processor_tests import TestHelper

class TestJumps(TestHelper):
    def test_jp(self):
        # given
        self.given_register_contains_value('a', 0x00)
        self.memory.poke(0xbeef, 0xcb)
        self.memory.poke(0xbef0, 0xff)

        self.given_next_instruction_is(0xc3, 0xef, 0xbe)

        # when
        self.processor.execute()
        self.processor.execute()

        # then
        self.assert_register('a').equals(0b10000000)
        self.assert_pc_address().equals(0xbef1)

    def test_jp_nz(self):
        for z_flag in [True, False]:
            yield self.check_jp_nz, z_flag

    def check_jp_nz(self, z_flag):
        # given
        self.processor.set_condition('z', z_flag)
        self.given_next_instruction_is(0xc2, 0xef, 0xbe)

        # when
        self.processor.execute()

        # then
        self.assert_pc_address().equals(0x0003 if z_flag else 0xbeef)

    def test_jp_z(self):
        for z_flag in [True, False]:
            yield self.check_jp_z, z_flag

    def check_jp_z(self, z_flag):
        # given
        self.processor.set_condition('z', z_flag)
        self.given_next_instruction_is(0xca, 0xef, 0xbe)

        # when
        self.processor.execute()

        # then
        self.assert_pc_address().equals(0xbeef if z_flag else 0x0003)

    def test_jp_nc(self):
        for c_flag in [True, False]:
            yield self.check_jp_nc, c_flag

    def check_jp_nc(self, c_flag):
        # given
        self.processor.set_condition('c', c_flag)
        self.given_next_instruction_is(0xd2, 0xef, 0xbe)

        # when
        self.processor.execute()

        # then
        self.assert_pc_address().equals(0x0003 if c_flag else 0xbeef)

    def test_jp_c(self):
        for c_flag in [True, False]:
            yield self.check_jp_c, c_flag

    def check_jp_c(self, c_flag):
        # given
        self.processor.set_condition('c', c_flag)
        self.given_next_instruction_is(0xda, 0xef, 0xbe)

        # when
        self.processor.execute()

        # then
        self.assert_pc_address().equals(0xbeef if c_flag else 0x0003)

    def test_jp_po(self):
        for p_flag in [True, False]:
            yield self.check_jp_po, p_flag

    def check_jp_po(self, p_flag):
        # given
        self.processor.set_condition('p', p_flag)
        self.given_next_instruction_is(0xe2, 0xef, 0xbe)

        # when
        self.processor.execute()

        # then
        self.assert_pc_address().equals(0x0003 if p_flag else 0xbeef)

    def test_jp_pe(self):
        for p_flag in [True, False]:
            yield self.check_jp_pe, p_flag

    def check_jp_pe(self, p_flag):
        # given
        self.processor.set_condition('p', p_flag)
        self.given_next_instruction_is(0xea, 0xef, 0xbe)

        # when
        self.processor.execute()

        # then
        self.assert_pc_address().equals(0xbeef if p_flag else 0x0003)

    def test_jp_p(self):
        for s_flag in [True, False]:
            yield self.check_jp_p, s_flag

    def check_jp_p(self, s_flag):
        # given
        self.processor.set_condition('s', s_flag)
        self.given_next_instruction_is(0xf2, 0xef, 0xbe)

        # when
        self.processor.execute()

        # then
        self.assert_pc_address().equals(0x0003 if s_flag else 0xbeef)

    def test_jp_m(self):
        for s_flag in [True, False]:
            yield self.check_jp_m, s_flag

    def check_jp_m(self, s_flag):
        # given
        self.processor.set_condition('s', s_flag)
        self.given_next_instruction_is(0xfa, 0xef, 0xbe)

        # when
        self.processor.execute()

        # then
        self.assert_pc_address().equals(0xbeef if s_flag else 0x0003)
