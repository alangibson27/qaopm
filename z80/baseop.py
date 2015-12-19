class BaseOp:
    def __init__(self):
        pass

    def execute(self):
        raise NotImplementedError("operation not implemented")

    def t_states(self):
        raise NotImplementedError("operation not implemented")

    def __str__(self):
        return 'unimplemented operation'
