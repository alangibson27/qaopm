#!/usr/bin/python
from z80.io import IO
from z80.processor import Processor
from memory.memory import Memory, load_memory
import argparse


def run():
    parser = argparse.ArgumentParser(description='Run a Z80 assembly program')
    parser.add_argument('sourcefile', metavar='sourcefile', type=str, help='Z80 binary file')
    parser.add_argument('--dumprange', type=str, help='Range of memory to dump', required=False)
    parser.add_argument('--verbose', '-v', help='Enable verbose output', required=False, action='store_true')
    args = parser.parse_args()

    memory = Memory()
    io = IO()
    processor = Processor(memory, io)

    load_memory(memory, args.sourcefile, 0x0000)

    t_states = 0
    while True:
        executed = processor.execute()
        if args.verbose:
            print(executed)
        else:
            print('.'),
        t_states += executed.t_states()

        if str(executed) == 'nop':
            break

    print('\n')
    print('Completed program execution in {} t-states'.format(t_states))
    print('Main register states:')
    for reg, value in processor.main_registers.items():
        print('{0:}: {1:#04x}\t\t').format(reg, value),

    print('\n')
    print('Alternate register states:')
    for reg, value in processor.alternate_registers.items():
        print('{0:}: {1:#04x}\t\t'.format(reg, value)),

    print('\n')
    print('Special register states:')
    for reg, value in processor.special_registers.items():
        print('{0:}: {1:#06x}\t\t'.format(reg, value)),

    if args.dumprange is not None:
        start = int(args.dumprange.split(':')[0], 16) & 0xffff
        end = int(args.dumprange.split(':')[1], 16) & 0xffff

        print('\n')
        print('Listing of memory values from {0:#06x} to {1:#06x}'.format(start, end))
        for addr in range(start, end + 1):
            print '{0:#06x}: {1:#04x}'.format(addr, memory.peek(addr))

if __name__ == '__main__':
    run()