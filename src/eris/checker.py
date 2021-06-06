from er_types import Type
from error_report import report, Location


class TypeInfo:
    def __init__(self, typ: Type, value=None):
        self.typ = typ
        self.val = value

    @staticmethod
    def err_type():
        return TypeInfo(Type._error)


class Symbol:
    def __init__(self, name: str, t_info: TypeInfo) -> Type:
        self.name = name
        self.type_info = t_info
        self.annotation = None


def as_type(typ_or_tinfo: TypeInfo or Type) -> Type:
    if isinstance(typ_or_tinfo, Type):
        return typ_or_tinfo
    assert isinstance(typ_or_tinfo, TypeInfo), "Impossible"
    return typ_or_tinfo.typ


BinOpRules = {
    'Add': [[Type.int, Type.int, Type.int],
            [Type.int, Type.float, Type.float],
            [Type.float, Type.float, Type.float],
            [Type.str, Type.str, Type.str]],

    'Sub': [[Type.int, Type.int, Type.int],
            [Type.float, Type.int, Type.float],
            [Type.float, Type.float, Type.float]],

    'Mult': [[Type.int, Type.int, Type.int],
             [Type.float, Type.int, Type.float],
             [Type.float, Type.float, Type.float]],

    'Div': [[Type.int, Type.int, Type.int],
            [Type.float, Type.int, Type.float],
            [Type.float, Type.float, Type.float]],
}


def op_tok(name):
    if name == 'Add':
        return '+'
    elif name == 'Mult':
        return '*'
    elif name == 'Sub':
        return '-'
    elif name == 'Div':
        return '/'

    return '?'


# TODO: Handle edge cases like division with zero
def find_binop_rule(left, op, right) -> TypeInfo:
    left = as_type(left)
    right = as_type(right)

    if not op in BinOpRules:
        return False

    rule = BinOpRules[op]

    for type_rule in rule:
        if left == type_rule[0] and right == type_rule[1]\
                or left == type_rule[1] and right == type_rule[0]:
            return TypeInfo(type_rule[2])

    return TypeInfo.err_type()


class Checker:
    def __init__(self, ast, src):
        self.ast = ast
        self.func_stack = []
        self.symbol_stack = []
        self.has_error = False
        self.src = src
        self.error_msg = None
        self.on_error = report

    def enter_scope(self):
        self.symbol_stack.append({})

    def exit_scope(self):
        self.symbol_stack.pop()

    def add_symbol(self, name: str, typ_info: TypeInfo):
        self.symbol_stack[-1][name] = Symbol(name, typ_info)

    def find_symbol(self, name) -> Symbol:
        for scope in self.symbol_stack[::-1]:
            if name in scope:
                return scope[name]

        return Symbol('<error>', TypeInfo(Type._error))

    def error_at():
        pass

    def error(self, msg: str, node):
        if self.has_error:
            return
        self.on_error(self.src, msg, node)
        self.has_error = True

        # Only store the first error message
        if not self.error_msg:
            self.error_msg = msg

    def check(self):
        self.enter_scope()
        for stat in self.ast.body:
            self.check_stat(stat)
            if self.has_error:
                return
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

    def check_assign(self, stat) -> TypeInfo:
        """Type checks [stat] and returns the type of the RHS"""
        lhs = stat.targets
        rhs = stat.value
        assert len(lhs) == 1, "Only single assignment statements are supported"

        # TODO: handle assignments where the RHS is *not* an identifier
        name = lhs[0].id

        existing = self.find_symbol(name)
        typ_info = self.check_exp(rhs)

        # TODO: handle type annotations.
        if existing.type_info.typ != Type._error:
            existing.type_info = typ_info
            return typ_info

        self.add_symbol(name, typ_info)
        return typ_info

    def check_exp(self, exp) -> TypeInfo:
        exp_kind = exp.__class__.__name__
        method_name = 'check_' + exp_kind.lower()
        method = getattr(self, method_name, None)

        if method is None:
            print('Skipping exp: ', exp_kind)
            return False

        return method(exp)

    def check_constant(self, exp) -> TypeInfo:
        """Type check [exp] and return it's TypeInfo. [exp] must be a constant."""
        typ = Type.primitives[exp.value.__class__.__name__]
        if not (typ is None):
            return TypeInfo(typ, exp.value)
        return TypeInfo(typ, exp.value)

    def check_name(self, exp) -> TypeInfo:
        name = exp.id
        typ = self.find_symbol(name).type_info
        return typ

    def check_binop(self, exp) -> TypeInfo:
        op_name = exp.op.__class__.__name__
        ltyp = self.check_exp(exp.left)
        rtyp = self.check_exp(exp.right)

        if not op_name in BinOpRules:
            self.error('Operator "' + op_name + '" Not supported yet')

        res_type_info = find_binop_rule(ltyp, op_name, rtyp)
        if res_type_info.typ == Type._error:
            err_str = f"operator '{op_tok(op_name)}' cannot be applied to '{ltyp.typ.tag}' and '{rtyp.typ.tag}'"
            self.error(err_str, exp)

        return res_type_info
