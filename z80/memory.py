class Memory:
    MEMORY_SIZE = 0x10000

    def __init__(self):
        self.memory = [0x0] * self.MEMORY_SIZE

    def poke(self, address, value):
        if value < 0x0 or value > 0xff:
            raise MemoryException("invalid value for poke")

        self.memory[address % self.MEMORY_SIZE] = value

    def peek(self, address):
        return self.memory[address % self.MEMORY_SIZE]

class MemoryException(Exception):
    pass