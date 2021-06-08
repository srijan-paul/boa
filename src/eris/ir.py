class Seq:
    def __init__(self):
        self.cmds = []


class Function:
    def __init__(self, name):
        self.name = name
        self.body = Seq()
        self.vars = []  # list of int (var ids)


class LocalVar:
    def __init__(self, id):
        self.id = id


class Value:
    pass


class Integer(Value):
    def __init__(self, value: int):
        self.value = value


class Float(Value):
    def __init__(self, value: float):
        self.value = value

class Cmd: pass

class Mov(Cmd):
    def __init__(self, dst: int, src: Value):
        self.dst = dst
        self.src = src