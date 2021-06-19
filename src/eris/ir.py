from er_types import *

class Seq:
    def __init__(self):
        self.cmds = []


class Func:
    def __init__(self, name, typ):
        self.name = name
        self.body = Seq()
        self.typ = typ
        self.vars = []  # list of int (var ids)

    def __str__(self):
        s = f'function {self.name}: {str(self.typ)}' + '{'
        for cmd in self.body.cmds:
            s += '\n\t' + str(cmd)
        return s + '\n}\n'


class Call:
    def __init__(self, func: Func, args):
        self.func = func
        self.args = args

    def __str__(self):
        return self.func.name + '(' + ', '.join([str(x) for x in self.args]) + ')'

    __repr__ = __str__

class Module:
    def __init__(self, name: str):
        self.name  = name
        self.funcs = []

        # top level function for toplevel code that
        # goes in main
        self.funcs.append(Func('main', TypeFunc([], TypeInt())))

    def __str__(name):
        return 'Module: ' + self.name

    __repr__ = __str__


class LocalVar:
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return 'x' + str(self.id)

    __repr__ = __str__


class Builtin:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

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
