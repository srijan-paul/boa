class Seq:
    def __init__(self):
        self.cmds = []


class Func:
    def __init__(self, name):
        self.name = name
        self.body = Seq()
        self.vars = []  # list of int (var ids)

    def __str__(self):
        s = 'function ' + self.name + ' {'
        for cmd in self.body.cmds:
            s += '\n\t' + str(cmd)
        return s + '\n}\n'


class LocalVar:
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return 'x' + str(self.id)

    __repr__ = __str__


class Value:
    pass


class Number(Value):
    def __init__(self, value: float):
        self.value = value

    def __str__(self):
        return str(self.value)

    __repr__ = __str__


class Cmd:
    pass


class Mov(Cmd):
    def __init__(self, dst: int, src: Value):
        self.dst = dst
        self.src = src

    def __str__(self):
        return 'x' + str(self.dst) + ' ← ' + str(self.src)

    __repr__ = __str__


class BinOp(Cmd):
    def __init__(self, dst, l, op, r):
        self.left = l
        self.right = r
        self.dst = dst
        self.op = op

    def __str__(self):
        return f'x{self.dst} ← {self.left} {self.op} {self.right}'
      
    __repr__ = __str__
