class BaseOp:
    def __init__(self):
        pass

    def execute(self, instruction_bytes):
        raise NotImplementedError("operation not implemented")

    def __str__(self):
        return 'unimplemented operation'


class Undocumented(BaseOp):
    def __init__(self, mnemonic):
        BaseOp.__init__(self)
        self.mnemonic = mnemonic

    def execute(self, instruction_bytes):
        raise NotImplementedError(self.mnemonic)

    def __str__(self):
        return self.mnemonic


class Nop(BaseOp):
    def __init__(self):
        BaseOp.__init__(self)

    def execute(self, instruction_bytes):
        return 4, False

    def __str__(self):
        return 'nop'

