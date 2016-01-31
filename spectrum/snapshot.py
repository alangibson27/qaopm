from memory.memory import load_memory_from_binary


def load_z80_v1_snapshot(file, processor, memory):
    def byte():
        return next_byte(snapshot_file)

    def lsb_word():
        return byte() | byte() << 8

    with open(file, 'r') as snapshot_file:
        processor.main_registers['a'] = byte()
        processor.main_registers['f'] = byte()
        processor.main_registers['c'] = byte()
        processor.main_registers['b'] = byte()
        processor.main_registers['l'] = byte()
        processor.main_registers['h'] = byte()
        processor.special_registers['pc'] = lsb_word()
        processor.special_registers['sp'] = lsb_word()
        processor.special_registers['i'] = byte()

        r_low_bits = byte() & 0b01111111
        indicator = byte()
        r_high_bit = (indicator & 0b1) << 7
        processor.special_registers['r'] = r_high_bit | r_low_bits
        border_colour = (indicator & 0b1110) >> 1
        memory_compressed = (indicator & 0b00100000) != 0

        processor.main_registers['e'] = byte()
        processor.main_registers['d'] = byte()

        processor.alternate_registers['c'] = byte()
        processor.alternate_registers['b'] = byte()
        processor.alternate_registers['e'] = byte()
        processor.alternate_registers['d'] = byte()
        processor.alternate_registers['l'] = byte()
        processor.alternate_registers['h'] = byte()
        processor.alternate_registers['a'] = byte()
        processor.alternate_registers['f'] = byte()

        processor.index_registers['iy'] = lsb_word()
        processor.index_registers['ix'] = lsb_word()

        processor.iff[0] = True if byte() > 0 else False
        processor.iff[1] = True if byte() > 0 else False

        indicator_2 = byte()
        processor.interrupt_mode = indicator_2 & 0b11

        if memory_compressed:
            load_memory_from_compressed_binary(memory, snapshot_file, 0x4000)
        else:
            load_memory_from_binary(memory, snapshot_file, 0x4000)

        end_marker = [byte(), byte(), byte(), byte()]
        if end_marker != [0x00, 0xed, 0xed, 0x00]:
            raise IOError(".z80 file format invalid")


def load_memory_from_compressed_binary(memory, binary_file, base):
    while base < 0x10000:
        byte = next_byte(binary_file)
        if byte == 0xed:
            byte_2 = next_byte(binary_file)
            if byte_2 == 0xed:
                repetitions = next_byte(binary_file)
                value = next_byte(binary_file)
                for i in xrange(0, repetitions):
                    memory[base] = value
                    base += 1
            else:
                memory[base] = byte
                memory[base + 1] = byte_2
                base += 2
        else:
            memory[base] = byte
            base += 1


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