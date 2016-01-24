import pygame
import time

from pygame.pixelarray import PixelArray

from memory.memory import Memory, load_memory
from spectrum.display_adapter import DisplayAdapter
from spectrum.snapshot import load_sna_snapshot
from z80.interrupt_operations import OpRetn
from z80.io import IO
from z80.processor import Processor


class DummyIO(IO):
    def read(self, port, high_byte):
        print 'read {}'.format(hex(port))
        return 0

    def write(self, port, high_byte, value):
        print 'write {}, {}'.format(hex(port), hex(value))


def start(rom_file, snapshot_file):
    memory = Memory()
    processor = Processor(memory, DummyIO())
    display_adapter = DisplayAdapter(memory)

    load_memory(memory, rom_file, 0x0000)
    load_sna_snapshot(snapshot_file, processor, memory)
    OpRetn(processor).execute()

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
    while i < 50:
        i += 1
        update_display(screen, display_adapter) + seconds_per_refresh
        t_states = 0
        while t_states < t_states_per_refresh:
            executed = processor.execute()
            t_states += executed.t_states()


def current_time_ms():
    return time.time()


def update_display(screen, display_adapter):
    for x in xrange(0, 256):
        for y in xrange(0, 192):
            screen[x][y] = display_adapter.pixel_at(x, y)
    pygame.display.flip()
    return current_time_ms()
