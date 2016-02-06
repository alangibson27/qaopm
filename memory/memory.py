from z80.funcs import to_signed, big_endian_value


class Memory:
    RAMTOP = 0xffff

    def __init__(self):
        self.memory = [0x0] * (self.RAMTOP + 1)

    def poke(self, address, value):
        if value < 0x0 or value > 0xff:
            raise MemoryException("invalid value for poke")

        self.memory[address & self.RAMTOP] = value

    def peek(self, address):
        return self.memory[address & self.RAMTOP]

    def block_peek(self, low, high):
        return self.memory[low & self.RAMTOP:high & self.RAMTOP]

class MemoryException(Exception):
    pass


def load_memory(memory, binary_file_name, base):
    with open(binary_file_name, 'rb') as binary_file:
        load_memory_from_binary(memory, binary_file, base)


def load_memory_from_binary(memory, binary_file, base):
    byte = binary_file.read(1)
    while byte != '':
        memory[base] = ord(byte)
        byte = binary_file.read(1)
        base = (base + 1) & 0xffff


def save_memory(memory, binary_file_name, start, length):
    with open(binary_file_name, 'wb') as binary_file:
        for i in range(0, length):
            binary_file.write(chr(memory[(start + length) & 0xffff]))


def fetch_byte(memory, pc):
    return memory[pc], (pc + 1) & 0xffff


def fetch_signed_byte(memory, pc):
    return to_signed(memory[pc]), (pc + 1) & 0xffff


def fetch_word(memory, pc):
    return big_endian_value([memory[pc], memory[(pc + 1) & 0xffff]]), (pc + 2) & 0xffff
