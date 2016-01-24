import os
from nose.tools import assert_equals

from spectrum.snapshot import load_sna_snapshot
from tests.processor.processor_tests import TestHelper


class TestSnapshotLoader(TestHelper):
    def test_load_sna_snapshot_reads_values_correctly(self):
        # when
        load_sna_snapshot(_this_directory() + '/test_snapshot.sna', self.processor, self.memory)

        # then
        self.assert_special_register('i').equals(0x3f)

        self.assert_alt_register_pair('hl').equals(0x3800)
        self.assert_alt_register_pair('de').equals(0xb800)
        self.assert_alt_register_pair('bc').equals(0x2017)
        self.assert_alt_register_pair('af').equals(0x4400)

        self.assert_register_pair('hl').equals(0xa810)
        self.assert_register_pair('de').equals(0xb95c)
        self.assert_register_pair('bc').equals(0x2117)

        self.assert_index_register('ix').equals(0x3a5c)
        self.assert_index_register('iy').equals(0xd403)

        assert_equals(self.processor.iff[1], False)

        self.assert_special_register('r').equals(0x26)

        self.assert_register_pair('af').equals(0x5c00)
        self.assert_register_pair('sp').equals(0x44ff)

        assert_equals(self.processor.interrupt_mode, 1)

        #assert_equals(self.border_colour, 7)

        # self.assert_memory(0x4020).contains(0x38)


def _this_directory():
    return os.path.dirname(os.path.abspath(__file__))
