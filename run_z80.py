from z80.io import IO
from z80.processor import Processor
from memory.memory import Memory, load_memory
import argparse

def run():
    parser = argparse.ArgumentParser(description='Run a Z80 assembly program')
    parser.add_argument('sourcefile', metavar='sourcefile', type=str, help='Z80 binary file')
    args = parser.parse_args()

    memory = Memory()
    io = IO()
    processor = Processor(memory, io)

    load_memory(memory, args.sourcefile, 0x0000)

    t_states = 0
    while True:
        executed = processor.execute()
        print(executed)
        t_states += executed.t_states()

        if str(executed) == 'nop':
            break

    print('Completed program execution in {} t-states'.format(t_states))
    print('Main register states:')
    for reg, value in processor.main_registers.items():
        print(reg + ': ' + hex(value))

    print('Alternate register states:')
    for reg, value in processor.alternate_registers.items():
        print(reg + ': ' + hex(value))

    print('Special register states:')
    for reg, value in processor.special_registers.items():
        print(reg + ': ' + hex(value))

if __name__ == '__main__':
    run()