import ir
from er_types import Type, TypeBool, TypeNum, TypeStr, types_consistent, Symbol, TypeInfo, TypeVar


def classname(obj):
    return obj.__class__.__name__


ir_op = {
    'Add': [['num', 'num', TypeNum], ['str', 'str', TypeStr]],
    'Div': [['num', 'num', TypeNum]],
    'Mult': [['num', 'num', TypeNum], ['str', 'num', TypeStr]],
    'Sub': [['num', 'num', TypeNum]]
}


def find_op_type(lhs, op, rhs):
    assert op in ir_op
    typs = ir_op[op]

    for typ in typs:
        if (lhs.tag == typ[0] and rhs.tag == typ[1]) or (rhs.tag == typ[0] and lhs.tag == typ[1]):
            return typ[2]()

    return None

class Dummy:
    pass

class DummyNode:
    def __init__(self, typ):
        assert isinstance(typ, Type)
        self._type = typ


class ToIR:
    def __init__(self):
        self.loc_id_of_decl = {}  # int -> ast.Name
        self.visited_decls = set()  # { ast.Name }
        self.module  = ir.Module('main')
        self.func    = self.module.funcs[0]

    def add_local(self, decl):
        """Adds a local variable referencing [decl] to the 
        body of the current function and returns an ID that can be
        used to refer to this local"""
        self.visited_decls.add(decl)
        self.func.vars.append(decl)
        return len(self.func.vars) - 1

    def add_temp_local(self, typ):
        self.func.vars.append(DummyNode(typ))
        return len(self.func.vars) - 1

    def emit(self, instr):
        self.func.body.cmds.append(instr)

    def do(self, module):
        for stat in module.body:
            self.do_stat(stat)
        print(self.func)

    def do_stat(self, stat):
        method_name = 'do_' + stat.__class__.__name__.lower()
        method = getattr(self, method_name, None)
        if method is None:
            print(f'toIR: skipping {stat.__class__.__name__}')
            return False

        method(stat)

    def do_assign(self, stat):
        lhs = stat.targets
        rhs = stat.value
        assert len(lhs) == 1, "Only single assignments are supported"

        lhs = lhs[0]

        # TODO: handle assignments where the RHS is not
        # an identifier
        if lhs in self.visited_decls:
            # assignment to existing variable
            id = self.loc_id_of_decl[lhs]
            self.emit(ir.Mov(id, self.do_exp(rhs)))
        else:
            # declare new variable in the current function's
            # scope
            val = self.do_exp(rhs)
            id = self.add_local(lhs)
            self.loc_id_of_decl[lhs] = id
            self.emit(ir.Mov(id, val))

    def do_annassign():
        pass

    def do_for():
        pass

    def do_exp(self, node):
        cname = classname(node)
        method_name = 'do_' + cname.lower()
        method = getattr(self, method_name, None)
        if not method:
            print(f'ToIR: Skipping Node: {cname}')
            return '<nop>'
        return method(node)

    def do_constant(self, node):
        val = node.value
        if type(val) == int or type(val) == float:
            return ir.Number(val)
        else:
            raise Exception("Not implemented")

    def do_binop(self, node):
        op = classname(node.op)
        lhs = self.do_exp(node.left)
        rhs = self.do_exp(node.right)

        assert op in ir_op, f"Invalid operator '{op}'"
        typ = find_op_type(node.left._type, op, node.right._type)
        assert typ

        loc_id = self.add_temp_local(typ)
        cmd = ir.Mov(loc_id, ir.BinOp(loc_id, lhs, self.op_to_s(op), rhs))
        self.emit(cmd)
        return ir.LocalVar(loc_id)

    def op_to_s(self, op):
        if op == 'Add':
            return '+'
        if op == 'Mult':
            return '*'
        if op == 'Div':
            return '/'
        if op == 'Sub':
            return '-'
        raise Exception("Not implemented")

    def do_name(self, node):
        key = node._type._decl
        loc_id = self.loc_id_of_decl[key]
        return ir.LocalVar(loc_id)
