from memory.memory import load_memory_from_binary


def load_sna_snapshot(file, processor, memory):
    with open(file, 'r') as snapshot_file:
        processor.special_registers['i'] = next_byte(snapshot_file)

        processor.alternate_registers['h'] = next_byte(snapshot_file)
        processor.alternate_registers['l'] = next_byte(snapshot_file)
        processor.alternate_registers['d'] = next_byte(snapshot_file)
        processor.alternate_registers['e'] = next_byte(snapshot_file)
        processor.alternate_registers['b'] = next_byte(snapshot_file)
        processor.alternate_registers['c'] = next_byte(snapshot_file)
        processor.alternate_registers['a'] = next_byte(snapshot_file)
        processor.alternate_registers['f'] = next_byte(snapshot_file)

        processor.main_registers['h'] = next_byte(snapshot_file)
        processor.main_registers['l'] = next_byte(snapshot_file)
        processor.main_registers['d'] = next_byte(snapshot_file)
        processor.main_registers['e'] = next_byte(snapshot_file)
        processor.main_registers['b'] = next_byte(snapshot_file)
        processor.main_registers['c'] = next_byte(snapshot_file)

        processor.index_registers['ix'] = next_word(snapshot_file)
        processor.index_registers['iy'] = next_word(snapshot_file)

        processor.iff[1] = (next_byte(snapshot_file) & 0b10) > 0

        processor.special_registers['r'] = next_byte(snapshot_file)

        processor.main_registers['a'] = next_byte(snapshot_file)
        processor.main_registers['f'] = next_byte(snapshot_file)

        processor.special_registers['sp'] = next_word(snapshot_file)

        processor.interrupt_mode = next_byte(snapshot_file)

        # not used yet
        border_colour = next_byte(snapshot_file)

        load_memory_from_binary(memory, snapshot_file, 0x4000)


def next_word(snapshot_file):
    return (next_byte(snapshot_file) << 8) | next_byte(snapshot_file)


def next_byte(snapshot_file):
    return ord(snapshot_file.read(1))