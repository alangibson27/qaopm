class BaseOp:
    def __init__(self):
        pass

    def execute(self):
        raise NotImplementedError("operation not implemented")

    def __str__(self):
        return 'unimplemented operation'


class Undocumented(BaseOp):
    def __init__(self, mnemonic):
        BaseOp.__init__(self)
        self.mnemonic = mnemonic

    def execute(self):
        raise NotImplementedError(self.mnemonic)

    def __str__(self):
        return self.mnemonic


class Nop(BaseOp):
    def __init__(self):
        BaseOp.__init__(self)

    def execute(self):
        return 4

    def __str__(self):
        return 'nop'

