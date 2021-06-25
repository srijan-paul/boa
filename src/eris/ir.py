from er_types import TypeFunc, TypeInt, TypeNum


class Seq:
    def __init__(self):
        self.cmds = []


class Stat:
    def __init__(self, cmd):
        self.cmd = cmd

    def __str__(self):
        return str(self.cmd)

    __repr__ = __str__


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
        self.name = name
        self.funcs = []

        # top level function for toplevel code that
        # goes in main
        self.funcs.append(Func('main', TypeFunc([], TypeInt())))

    def __str__(self):
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


class String(Value):
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return self.value

    __repr__ = __str__


class Bool(Value):
    def __init__(self, value: bool):
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


class Not(Cmd):
    def __init__(self, dst, src):
        self.dst = dst
        self.src = src

    def __str__(self):
        return f'not {src}'

    __repr__ = __str__


class For:
    def __init__(self, var, from_, to, step, body):
        self.var = var
        self.from_ = from_
        self.to = to
        self.step = step or Number(1)
        self.body = body

    def __str__(self):
        return f'for i = {self.from_}, {self.to}, {self.step}:\n{str(self.body)}'

    __repr__ = __str__


class While:
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def __str__(self):
        return f'WHILE ({self.cond}) DO\n{self.body}\nEND'

    __repr__ = __str__


class If:
    def __init__(self, cond_exp, then: Seq):
        self.cond = cond_exp
        self.then = then

    def __str__(self):
        return f'IF [{self.cond}] -> {{\n {self.then} \n}}'

    __repr__ = __str__


class Break:
    def __init__(self):
        pass

    def __str__(self):
        return 'brk'

    __repr__ = __str__

