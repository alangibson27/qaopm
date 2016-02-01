import pygame
import time

from pygame.pixelarray import PixelArray

from memory.memory import Memory, load_memory
from spectrum.display_adapter import DisplayAdapter
from spectrum.snapshot import load_sna_snapshot, load_z80_v1_snapshot
from z80.interrupt_operations import OpRetn
from z80.io import IO
from z80.processor import Processor, InterruptRequest


class DummyIO(IO):
    def read(self, port, high_byte):
        # print 'read {}'.format(hex(port))
        return 191

    def write(self, port, high_byte, value):
        pass
        # print 'write {}, {}'.format(hex(port), hex(value))


def start(rom_file, snapshot_file):
    memory = [0x00] * 0x10000
    processor = Processor(memory, DummyIO())
    display_adapter = DisplayAdapter(memory)

    load_memory(memory, rom_file, 0x0000)
    load_z80_v1_snapshot(snapshot_file, processor, memory)

    pygame.init()
    size = 256, 192
    screen = pygame.display.set_mode(size)

    run_loop(processor, PixelArray(screen), display_adapter)

def run_loop(processor, screen, display_adapter):
    processor_clock_hz = 4000000
    seconds_per_refresh = 0.02
    time_per_t_state = 1.0 / processor_clock_hz
    t_states_per_refresh = seconds_per_refresh / time_per_t_state

    i = 0
    while 1:
        i += 1
        update_display(screen, display_adapter) + seconds_per_refresh
        t_states = 0
        processor.interrupt(InterruptRequest(irq_ack))
        while t_states < t_states_per_refresh:
            t_states += processor.execute()


def irq_ack():
    pass


def current_time_ms():
    return time.time()


def update_display(screen, display_adapter):
    display_adapter.update_display(screen)
    pygame.display.flip()
    return current_time_ms()
