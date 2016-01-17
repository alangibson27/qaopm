class BaseOp:
    def __init__(self):
        pass

    def execute(self):
        raise NotImplementedError("operation not implemented")

    def t_states(self):
        raise NotImplementedError("operation not implemented")

    def __str__(self):
        return 'unimplemented operation'


class CondOp(BaseOp):
    def __init__(self):
        BaseOp.__init__(self)
        self.last_t_states = None

    def t_states(self):
        return self.last_t_states


class Nop(BaseOp):
    def __init__(self):
        BaseOp.__init__(self)

    def execute(self):
        pass

    def t_states(self):
        return 4

    def __str__(self):
        return 'nop'

