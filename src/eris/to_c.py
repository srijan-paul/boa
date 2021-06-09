import ir


class Coder:
    def __init__(self):
        self.ccode = ''

    def render(self, fmt: str, vars: dict):
        self.ccode += fmt

    def emit_Mov(self): pass
