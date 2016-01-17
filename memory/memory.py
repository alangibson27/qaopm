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


class MemoryException(Exception):
    pass


def load_memory(memory, binary_file_name, base):
    with open(binary_file_name, 'rb') as binary_file:
        byte = binary_file.read(1)
        while byte != '':
            memory.poke(base, ord(byte))
            byte = binary_file.read(1)
            base = (base + 1) & 0xffff


def save_memory(memory, binary_file_name, start, length):
    with open(binary_file_name, 'wb') as binary_file:
        for i in range(0, length):
            binary_file.write(chr(memory.peek((start + length)) & 0xffff))
