class Memory:
    def __init__(self):
        self.memory = [0x0] * 0x10000

    def poke(self, address, value):
        if address < 0x0 or address > 0xffff:
            raise MemoryException("invalid address for poke")

        if value < 0x0 or value > 0xff:
            raise MemoryException("invalid value for poke")

        self.memory[address] = value

    def peek(self, address):
        if address < 0x0 or address > 0xffff:
            raise MemoryException("invalid address for peek")
        return self.memory[address]

class MemoryException(Exception):
    pass