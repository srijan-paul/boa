import ir
import ast
from er_types import Type, TypeBool, TypeNum, TypeStr, types_consistent, Symbol, TypeInfo, TypeVar
from builtins_ import builtins
from error_report import report


def classname(obj):
    return obj.__class__.__name__


ir_op = {
    'Add': [['num', 'num', TypeNum], ['str', 'str', TypeStr]],
    'Div': [['num', 'num', TypeNum]],
    'Mult': [['num', 'num', TypeNum], ['str', 'num', TypeStr]],
    'Sub': [['num', 'num', TypeNum]],
    'Lt': [['num', 'num', TypeNum]],
    'LtE': [['num', 'num', TypeNum]],
    'GtE': [['num', 'num', TypeNum]],
    'Gt': [['num', 'num', TypeNum]]
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
        self.module = ir.Module('main')
        self.func = self.module.funcs[0]
        self.body = self.func.body
        self.has_error = False

    def error(self, msg, node):
        if self.has_error:
            return
        report(self.src, msg, node)
        self.has_error = True

    def add_local(self, decl):
        """Adds a local variable referencing [decl] to the 
        body of the current function and returns an ID that can be
        used to refer to this local"""
        self.visited_decls.add(decl)
        self.func.vars.append(decl)

        loc_id = len(self.func.vars) - 1

        self.loc_id_of_decl[decl] = loc_id
        # used for debug comment generation
        decl._text = ast.get_source_segment(self.src, decl)
        return loc_id

    def add_temp_local(self, typ, node):
        dnode = DummyNode(typ)
        self.func.vars.append(dnode)
        dnode._text = ast.get_source_segment(self.src, node)

        loc_id = len(self.func.vars) - 1
        self.loc_id_of_decl[dnode] = loc_id
        return loc_id

    def emit(self, instr):
        self.body.cmds.append(instr)

    def do(self, module, src):
        self.ast = module
        self.src = src
        for stat in module.body:
            self.do_stat(stat)
        # print(self.func)

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

        assert '_decl' in lhs[0].__dict__, ast.get_source_segment(self.src, lhs[0]) + f" <- has no decl [line {lhs[0].lineno}] "
        lhs_decl = lhs[0]._decl

        # TODO: handle assignments where the RHS is not
        # an identifier
        if lhs_decl in self.visited_decls:
            # assignment to existing variable
            id = self.loc_id_of_decl[lhs_decl]
            self.emit(ir.Mov(id, self.do_exp(rhs)))
        else:
            # declare new variable in the current function's
            # scope
            val = self.do_exp(rhs)
            id = self.add_local(lhs_decl)
            self.emit(ir.Mov(id, val))

    def compile_block(self, stats: list) -> ir.Seq:
        """Compiles a list of statements into ir.Seq"""

        body = ir.Seq()
        prev_body = self.body

        self.body = body
        for stat in stats:
            self.do_stat(stat)

        self.body = prev_body
        return body

    def do_for(self, stat):
        iter_var = stat.target
        loc_id = self.add_local(iter_var)
        # print(iter_var)

        iter_call = stat.iter

        from_ = self.do_exp(iter_call.args[0])
        to = self.do_exp(iter_call.args[1])
        step = self.do_exp(iter_call.args[2]) if len(iter_call.args) == 3 else None

        body = self.compile_block(stat.body)
        self.emit(ir.For(ir.LocalVar(loc_id), from_, to, step, body))

    def do_while(self, stat):
        cond_exp = self.do_exp(stat.test)
        body     = self.compile_block(stat.body)
        self.emit(ir.While(cond_exp, body))

    def do_if(self, stat):
        cond_exp = self.do_exp(stat.test)
        body = self.compile_block(stat.body)
        self.emit(ir.If(cond_exp, body))

    def do_annassign():
        pass

    def do_exp(self, node):
        cname = classname(node)
        method_name = 'do_' + cname.lower()
        method = getattr(self, method_name, None)
        if not method:
            print(f'ToIR: Skipping Node: {cname}')
            return '<nop>'
        return method(node)

    def do_expr(self, expr):
        self.emit(ir.Stat(self.do_exp(expr.value)))

    def do_call(self, call_exp):
        func = self.do_exp(call_exp.func)
        args = [self.do_exp(arg) for arg in call_exp.args]
        return ir.Call(func, args)

    def do_constant(self, node):
        val = node.value
        if type(val) == int or type(val) == float:
            return ir.Number(val)
        elif type(val) == str:
            return ir.String(val)
        elif type(val) == bool:
            return ir.Bool(val)
        else:
            raise Exception("Not implemented")

    def do_binop(self, node):
        op = classname(node.op)
        lhs = self.do_exp(node.left)
        rhs = self.do_exp(node.right)

        assert op in ir_op, f"Invalid operator '{op}'"
        typ = find_op_type(node.left._type, op, node.right._type)
        assert typ, f"Could not resolve binary operator '{self.op_to_s(op)}' for '{node.left._type}' and '{node.right._type}'"

        loc_id = self.add_temp_local(typ, node)
        cmd = ir.Mov(loc_id, ir.BinOp(loc_id, lhs, self.op_to_s(op), rhs))
        self.emit(cmd)
        return ir.LocalVar(loc_id)

    def do_compare(self, node: ast.If):
        lhs = node.left
        rhs = node.comparators[0]
        op = classname(node.ops[0])

        assert op in ir_op, f"Invalid operator '{op}'"
        typ = find_op_type(lhs._type, op, rhs._type)
        assert typ, f"Could not resolve binary operator '{self.op_to_s(op)}' for '{lhs._type}' and '{rhs._type}'"

        loc_id = self.add_temp_local(typ, node)
        left  = self.do_exp(lhs)
        right = self.do_exp(rhs)
        cmd = ir.Mov(loc_id, ir.BinOp(loc_id, left, self.op_to_s(op), right))
        self.emit(cmd)
        return ir.LocalVar(loc_id)

    def op_to_s(self, op):
        op_map = {
            'Add': '+',
            'Mult': '*',
            'Div': '/',
            'Sub': '-',
            'Lt': '<',
            'Gt': '>',
            'LtE': '<=',
            'GtE': '>=',
        }
    
        if op in op_map:
            return op_map[op]

        raise Exception("Not implemented")

    def do_name(self, node):
        if node.id in builtins:
            return ir.Builtin(node.id)

        if not getattr(node, '_decl', False):
            self.error("INTERNAL: ast not type annotated", node)
            return
        decl = node._decl
        # print(key, node.id)
        loc_id = self.loc_id_of_decl[decl]
        return ir.LocalVar(loc_id)
