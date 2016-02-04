from z80.bit import *
from z80.rotate import *
from z80.shift import *


class OpIndexedCbGroup(BaseOp):
    def __init__(self, register, processor, memory):
        BaseOp.__init__(self)
        self.last_t_states = None
        self.processor = processor

        self.ops = {
            0x06: OpRlcIndexedIndirect(processor, memory, register),
            0x0e: OpRrcIndexedIndirect(processor, memory, register),
            0x16: OpRlIndexedIndirect(processor, memory, register),
            0x1e: OpRrIndexedIndirect(processor, memory, register),
            0x26: OpSlaIndexedIndirect(processor, memory, register),
            0x2e: OpSraIndexedIndirect(processor, memory, register),
            0x3e: OpSrlIndexedIndirect(processor, memory, register),

            0x46: OpBitIndexedIndirect(processor, memory, register, 0),
            0x4e: OpBitIndexedIndirect(processor, memory, register, 1),
            0x56: OpBitIndexedIndirect(processor, memory, register, 2),
            0x5e: OpBitIndexedIndirect(processor, memory, register, 3),
            0x66: OpBitIndexedIndirect(processor, memory, register, 4),
            0x6e: OpBitIndexedIndirect(processor, memory, register, 5),
            0x76: OpBitIndexedIndirect(processor, memory, register, 6),
            0x7e: OpBitIndexedIndirect(processor, memory, register, 7),

            0x86: OpResIndexedIndirect(processor, memory, register, 0),
            0x8e: OpResIndexedIndirect(processor, memory, register, 1),
            0x96: OpResIndexedIndirect(processor, memory, register, 2),
            0x9e: OpResIndexedIndirect(processor, memory, register, 3),
            0xa6: OpResIndexedIndirect(processor, memory, register, 4),
            0xae: OpResIndexedIndirect(processor, memory, register, 5),
            0xb6: OpResIndexedIndirect(processor, memory, register, 6),
            0xbe: OpResIndexedIndirect(processor, memory, register, 7),

            0xc6: OpSetIndexedIndirect(processor, memory, register, 0),
            0xce: OpSetIndexedIndirect(processor, memory, register, 1),
            0xd6: OpSetIndexedIndirect(processor, memory, register, 2),
            0xde: OpSetIndexedIndirect(processor, memory, register, 3),
            0xe6: OpSetIndexedIndirect(processor, memory, register, 4),
            0xee: OpSetIndexedIndirect(processor, memory, register, 5),
            0xf6: OpSetIndexedIndirect(processor, memory, register, 6),
            0xfe: OpSetIndexedIndirect(processor, memory, register, 7),
        }

    def execute(self, instruction_bytes):
        index_byte = instruction_bytes.popleft()
        op = self.ops[instruction_bytes.popleft()]
        instruction_bytes.appendleft(index_byte)
        return op.execute(instruction_bytes)

    def __str__(self):
        return 'INDEXED CB GROUP'

