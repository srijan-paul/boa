from py_types import Type


class Symbol:
    def __init__(self, name: str, type: Type) -> Type:
        self.name = name
        self.type = type


BinOpRules = {
    'Add': [[Type.int, Type.int, Type.int],
            [Type.int, Type.float, Type.float],
            [Type.float, Type.float, Type.float],
            [Type.str, Type.str, Type.str]],
    'Sub': [[Type.int, Type.int, Type.int],
            [Type.float, Type.int, Type.float],
            [Type.float, Type.float, Type.float]]
}


def find_binop_rule(left, op, right):
    if not op in BinOpRules:
        return False

    rule = BinOpRules[op]

    for typ in rule:
        if left == typ[0] and right == typ[1]:
            return type[2]

    return Type._error 


class Checker:
    def __init__(self, ast):
        self.ast = ast
        self.func_stack = []
        self.symbol_stack = []

    def enter_scope(self):
        self.symbol_stack.append({})

    def exit_scope(self):
        self.symbol_stack.pop()

    def add_symbol(self, name: str, type: Type):
        self.symbol_stack[-1][name] = Symbol(name, type)

    def find_symbol(self, name):
        for scope in self.symbol_stack[::-1]:
            if name in scope:
                return scope[name].type

        return Type._error

    def check(self):
        self.enter_scope()
        for stat in self.ast.body:
            self.check_stat(stat)
        self.exit_scope()

    def check_stat(self, node):
        node_name = node.__class__.__name__
        method_name = 'check_' + node_name.lower()
        method = getattr(Checker, method_name, None)
        if method is None:
            print('skipping node: ', node_name)
            return
        method(self, node)

    def check_functiondef(self, node):
        fname = node.name
        args = node.args
        raise "Not implemented"

    def check_return(self, stat):
        pass

    def check_assign(self, stat):
        lhs = stat.targets
        rhs = stat.value
        assert len(lhs) == 1, "Only single assignment statements are supported"
        name = lhs[0].id
        typ = self.check_exp(rhs)
        self.add_symbol(name, typ)
        return typ

    def check_exp(self, exp) -> Type:
        exp_kind = exp.__class__.__name__
        method_name = 'check_' + exp_kind.lower()
        method = getattr(self, method_name, None)
        if method is None:
            print('Skipping exp: ', exp_kind)
            return False
        return method(exp)

    def check_constant(self, exp) -> Type:
        typ = Type.primitives[exp.value.__class__.__name__]
        if not (type is None):
            return typ
        return Type.any

    def check_name(self, exp):
        name = exp.id
        typ = self.find_symbol(name)
        return typ

    def check_binop(self, exp) -> Type:
        op_name = exp.op.__class__.__name__
        ltyp = self.check_exp(exp.left)
        rtyp = self.check_exp(exp.right)

        if not BinOpRules[op_name]:
            raise 'Operator ' + op_name + ' Not supported yet'

        typ = find_binop_rule(ltyp , op_name, rtyp)
        if typ == Type._error:
            raise Exception('Bad binary op')

        return typ
