from nose.tools import assert_false, assert_true
from processor_tests import TestHelper
from z80.processor import InterruptRequest


class AckReceiver:
    def __init__(self):
        self.ack = False

    def acknowledge(self):
        self.ack = True


class TestInterrupts(TestHelper):
    def test_im0_invoked_when_maskable_interrupts_enabled(self):
        # given
        self.maskable_interrupts_are_enabled()
        self.maskable_interrupt_mode_is(0)
        self.given_stack_pointer_is(0xffff)

        ack_receiver = self.an_im0_interrupt_is_generated()

        # when
        self.processor.execute()

        # then
        assert_true(ack_receiver.ack)
        self.assert_pc_address().equals(0xbeef)
        self.assert_stack_pointer().equals(0xfffd)
        self.assert_memory(0xfffd).contains(0x03)
        self.assert_memory(0xfffe).contains(0x00)

    def test_im0_not_invoked_when_maskable_interrupts_disabled(self):
        # given
        self.maskable_interrupts_are_disabled()
        self.maskable_interrupt_mode_is(0)
        self.given_stack_pointer_is(0xffff)

        self.given_next_instruction_is(0xcb, 0xc0)

        ack_receiver = self.an_im0_interrupt_is_generated()

        # when
        self.processor.execute()

        # then
        assert_false(ack_receiver.ack)
        self.assert_pc_address().equals(0x0005)
        self.assert_register('b').equals(0x01)
        self.assert_stack_pointer().equals(0xffff)

    def test_im1_invoked_when_maskable_interrupts_enabled(self):
        # given
        self.maskable_interrupts_are_enabled()
        self.given_stack_pointer_is(0xffff)

        self.maskable_interrupt_mode_is(1)
        self.given_next_instruction_is(0xcb, 0xc0)

        ack_receiver = self.an_im1_interrupt_is_generated()

        # when
        self.processor.execute()

        # then
        assert_true(ack_receiver.ack)
        self.assert_pc_address().equals(0x0038)
        self.assert_stack_pointer().equals(0xfffd)
        self.assert_memory(0xfffd).contains(0x03)
        self.assert_memory(0xfffe).contains(0x00)
        self.assert_register('b').equals(0)

    def test_im1_not_invoked_when_maskable_interrupts_disabled(self):
        # given
        self.maskable_interrupts_are_disabled()
        self.given_stack_pointer_is(0xffff)

        self.maskable_interrupt_mode_is(1)
        self.given_next_instruction_is(0xcb, 0xc0)

        ack_receiver = self.an_im1_interrupt_is_generated()

        # when
        self.processor.execute()

        # then
        assert_false(ack_receiver.ack)
        self.assert_pc_address().equals(0x0005)
        self.assert_stack_pointer().equals(0xffff)
        self.assert_register('b').equals(0x01)

    def test_im2_invoked_when_maskable_interrupts_enabled(self):
        # given
        self.maskable_interrupts_are_enabled()
        self.given_stack_pointer_is(0xffff)

        self.maskable_interrupt_mode_is(2)
        self.given_next_instruction_is(0xcb, 0xc0)

        self.memory.poke(0xb0e0, 0xef)
        self.memory.poke(0xb0e1, 0xbe)

        self.given_register_contains_value('i', 0xb0)
        self.given_register_contains_value('r', 0xe1)

        ack_receiver = self.an_im2_interrupt_is_generated()

        # when
        self.processor.execute()

        # then
        assert_true(ack_receiver.ack)
        self.assert_pc_address().equals(0xbeef)
        self.assert_stack_pointer().equals(0xfffd)
        self.assert_memory(0xfffd).contains(0x03)
        self.assert_memory(0xfffe).contains(0x00)
        self.assert_register('b').equals(0x00)

    def test_im2_not_invoked_when_maskable_interrupts_enabled(self):
        # given
        self.maskable_interrupts_are_disabled()
        self.given_stack_pointer_is(0xffff)

        self.maskable_interrupt_mode_is(2)
        self.given_next_instruction_is(0xcb, 0xc0)

        self.memory.poke(0xb0e0, 0xef)
        self.memory.poke(0xb0e1, 0xbe)

        self.given_register_contains_value('i', 0xb0)
        self.given_register_contains_value('r', 0xe1)

        ack_receiver = self.an_im2_interrupt_is_generated()

        # when
        self.processor.execute()

        # then
        assert_false(ack_receiver.ack)
        self.assert_pc_address().equals(0x0005)
        self.assert_stack_pointer().equals(0xffff)
        self.assert_register('b').equals(0x01)

    def test_nmi_when_maskable_interrupts_disabled(self):
        # given
        self.maskable_interrupts_are_disabled()
        self.given_stack_pointer_is(0xffff)

        # nmi service routine
        self.memory.poke(0x0066, 0xcb)
        self.memory.poke(0x0067, 0xc7)

        # when
        self.processor.nmi()
        self.an_im0_interrupt_is_generated([0xdf])
        self.processor.execute()

        # then
        self.assert_pc_address().equals(0x0068)
        self.assert_register('a').equals(0x01)

        self.assert_stack_pointer().equals(0xfffd)
        self.assert_memory(0xfffd).contains(0x01)
        self.assert_memory(0xfffe).contains(0x00)

    def test_nmi_when_maskable_interrupts_enabled(self):
        # given
        self.maskable_interrupts_are_enabled()
        self.given_stack_pointer_is(0xffff)

        # nmi service routine
        self.memory.poke(0x0066, 0xcb)
        self.memory.poke(0x0067, 0xc7)

        # when
        self.processor.nmi()
        self.an_im0_interrupt_is_generated([0xdf])
        self.processor.execute()

        # then
        self.assert_pc_address().equals(0x0068)
        self.assert_register('a').equals(0x01)

        self.assert_stack_pointer().equals(0xfffd)
        self.assert_memory(0xfffd).contains(0x01)
        self.assert_memory(0xfffe).contains(0x00)

    def test_halt(self):
        assert_true(False)

    def test_reti(self):
        assert_true(False)

    def test_retn(self):
        assert_true(False)

    def maskable_interrupts_are_enabled(self):
        self.given_next_instruction_is(0xfb)
        self.processor.execute()

    def maskable_interrupts_are_disabled(self):
        self.given_next_instruction_is(0xf3)
        self.processor.execute()

    interrupt_mode_op_codes = {0: [0xed, 0x46], 1: [0xed, 0x56], 2: [0xed, 0x5e]}

    def maskable_interrupt_mode_is(self, mode):
        self.given_next_instruction_is(self.interrupt_mode_op_codes[mode])
        self.processor.execute()

    def an_im0_interrupt_is_generated(self, im0_data=[0xc3, 0xef, 0xbe]):
        ack_receiver = AckReceiver()
        request = InterruptRequest(ack_receiver.acknowledge, lambda: im0_data)
        self.processor.interrupt(request)
        return ack_receiver

    def an_im1_interrupt_is_generated(self):
        ack_receiver = AckReceiver()
        request = InterruptRequest(ack_receiver.acknowledge)
        self.processor.interrupt(request)
        return ack_receiver

    def an_im2_interrupt_is_generated(self):
        ack_receiver = AckReceiver()
        request = InterruptRequest(ack_receiver.acknowledge)
        self.processor.interrupt(request)
        return ack_receiver