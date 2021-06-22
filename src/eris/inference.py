import ast
from er_types import TypeVar, TypeStr, TypeInt, TypeNum, TypeBool, Type, types_equal
import debug
from error_report import report
from builtins_ import builtins
import textwrap


def visitor_error(self, msg, node):
    report(self.src, msg, node)
    self.has_error = True
    self.errmsg = self.errmsg or msg


ast.NodeVisitor.error = visitor_error


def classname(obj):
    return obj.__class__.__name__


class TypeGenerator(ast.NodeVisitor):
    def __init__(self, src):
        self.func_stack = []
        self.has_error = False
        self.eqs = []
        self.src = src
        self.errmsg = False

        self.symtab = {}  # str -> Type
        self.decl_of_name = {}  # str -> ast.Node

        # Used to generate the Type variables
        self.next_var_id = 0

    def add_typ(self, node, typvar: TypeVar):
        node._type = TypeVar

    def generate_var(self):
        self.next_var_id += 1
        return TypeVar(self.next_var_id)

    def assign_typvar(self, node):
        node._type = self.generate_var()

    # Visitor methods

    def visit_Module(self, module):
        for stat in module.body:
            self.visit(stat)
            if self.has_error:
                break

        return self.symtab

    def visit_Assign(self, stat: ast.Assign):
        if len(stat.targets) != 1:
            self.error("Only single single assignments are supported", stat)
            return

        if classname(stat.targets[0]) != 'Name':
            self.error("Only single variable assignments are supported", stat.targets[0])

        name = stat.targets[0]
        rhs = stat.value
        typ = self.visit(rhs)

        # Differentiate between Re-assignment and declaration
        if not name.id in self.decl_of_name:
            # Register this as a declaration in the symbol table
            self.decl_of_name[name.id] = name
            self.symtab[name.id] = typ
            typ._decl = name

        # TODO: check type consistency for re-assignments
        name._decl = self.decl_of_name[name.id]
        name._type = typ

    def visit_stats(self, stats):
        for stat in stats:
            self.visit(stat)
            if self.has_error:
                return

    # Infer types from blocks containing `return` statements
    def visit_For(self, stat: ast.For):
        iter_var = stat.target
        assert isinstance(iter_var, ast.Name), "Only variable iterators are supported"

        self.symtab[iter_var.id] = TypeNum()
        iter_var._type = self.symtab[iter_var.id]
        self.symtab[iter_var.id]._decl = iter_var

        iter_call = stat.iter
        if not isinstance(iter_call, ast.Call) or not isinstance(iter_call.func, ast.Name) or iter_call.func.id != 'range':
            self.error("only 'range' based for loops are supported right now.", iter_call)
            return False

        if len(iter_call.args) != 2 and len(iter_call.args) != 3:
            self.error(f"expected 2-3 arguments for range based for-loop (found {len(iter_call.args)})", iter_call)
            return False

        self.visit(iter_call.args[0])
        self.visit(iter_call.args[1])
        if len(iter_call.args) == 3:
            self.visit(iter_call.args[2])

        self.visit_stats(stat.body)

    # TODO: optimize trivial operations like 1 * 2, or other
    # cases where the LHS and RHS types are known
    def visit_BinOp(self, node: ast.BinOp):
        op = classname(node.op)
        self.visit(node.left)
        self.visit(node.right)

        if not op in ['Add', 'Mult', 'Sub', 'Div']:
            self.error(f"Operator '{op}' not supported", node)

        self.assign_typvar(node)
        return node._type

    def visit_Name(self, node: ast.Name):
        iden = node.id
        if iden in self.symtab:
            node._type = self.symtab[iden]
            node._decl = self.decl_of_name[iden]
            return node._type

        if iden in builtins:
            node._type = builtins[iden].typ
            node._decl = None
            return builtins[iden].typ

        self.error(f"Unknown variable '{id}'", node)

    def visit_Expr(self, node):
        self.visit(node.value)

    def visit_Call(self, node):
        self.visit(node.func)
        for arg in node.args:
            self.visit(arg)

        # TODO: support function types
        node._type = None

    # TODO: support - float, None
    def visit_Constant(self, node: ast.Constant):
        assert(classname(node) == 'Constant')
        val = node.value
        if type(val) == str:
            node._type = TypeStr()
        elif type(val) == int or type(val) == float:
            node._type = TypeNum()
        elif Type(val) == bool:
            node._type = TypeBool()
        else:
            self.error("Literal not supported", node)
            return TypeError()

        return node._type

    def generic_visit(self, node):
        print(f'EqGenerator: Skipping node {node.__class__.__name__}')


class Equation:
    def __init__(self, lhs, rhs, node):
        self.lhs = lhs
        self.rhs = rhs
        self.node = node

    def __str__(self):
        return str(self.lhs).ljust(4) + ' :: ' + str(self.rhs).rjust(4)

    __repr__ = __str__


class EqGenerator(ast.NodeVisitor):
    def __init__(self, ast):
        self.eqs = []
        self.ast = ast
        self.has_error = False

    def generate(self):
        self.visit(self.ast)
        return self.eqs

    def visit_Module(self, node: ast.Module):
        for stat in node.body:
            self.visit(stat)

    def visit_Name(self, _):
        pass  # Name types are resolved in the type var generation pass

    def visit_stats(self, stats: list):
        for stat in stats:
            self.visit(stat)

    def visit_Assign(self, node):
        # TODO: handle RHS that isn't a single symbol
        self.visit(node.value)

    def visit_Constant(self, node):
        assert not isinstance(node._type, TypeVar)

    def visit_Expr(self, exp):
        self.visit(exp.value)

    def visit_Call(self, call_exp):
        self.visit(call_exp.func)
        for arg in call_exp.args:
            self.visit(arg)

    def visit_For(self, stat):
        iter_var = stat.target
        assert isinstance(iter_var, ast.Name), "Only variable iterators are supported"

        iter_call = stat.iter
        if not isinstance(iter_call, ast.Call) or not isinstance(iter_call.func, ast.Name) or iter_call.func.id != 'range':
            self.error("only 'range' based for loops are supported right now.", iter_call)
            return False

        if len(iter_call.args) != 2 and len(iter_call.args) != 3:
            self.error(f"expected 2-3 arguments for range based for-loop (found {len(iter_call.args)})", iter_call)
            return False

        self.visit(iter_call.args[0])
        self.visit(iter_call.args[1])
        if len(iter_call.args) == 3:
            self.visit(iter_call.args[2])

        self.visit_stats(stat.body)

    # TODO: add type traits

    def visit_BinOp(self, node):
        """
        Generate type equations from binary operator application nodes.
        The constraints (simplified for initial version) are:
            - +  : (int, int) -> int
            - -  : (int, int) -> int
            - *  : (int, int) -> int
            - /  : (int, int) -> int
            - %  : (int, int) -> int
            - >  : (int, int) -> bool
            - <  : (int, int) -> bool
            - >= : (int, int) -> bool
            - <= : (int, int) -> bool
            - == : (T, T) -> bool
            - != : (T, T) -> bool
        """
        self.visit(node.left)
        self.visit(node.right)

        self.eqs.append(Equation(node.left._type, TypeNum(), node.left))
        self.eqs.append(Equation(node.right._type, TypeNum(), node.right))
        self.eqs.append(Equation(node._type, TypeNum(), node))

    def generic_visit(self, node):
        print(f'Eq generation: skipping: {classname(node)}')


# TODO: get rid of this dirty global variable by moving it to local state.
g_src = None
g_unify_error = None
def unification_error(err: str, node):
    global g_unify_error, g_src

    if g_unify_error: return
    g_unify_error = err 
    report(g_src, err, node)

def unify_var(typvar: Type, typ: Type, typmap: dict):
    assert isinstance(typvar, TypeVar)
    if typvar.tag in typmap:
        return unify(typmap[typvar], typ, typmap)

    typmap[typvar.tag] = typ
    return typmap, True


def unify(l_type: Type, r_type: Type, typmap: dict, node):
    if typmap is None:
        return typmap, False

    if types_equal(l_type, r_type):
        return typmap, True

    if isinstance(l_type, TypeVar):
        return unify_var(l_type, r_type, typmap)
    elif isinstance(r_type, TypeVar):
        return unify_var(r_type, l_type, typmap)
    else:
        unification_error(f"Could not unify type '{r_type}' with '{l_type}'", node)
        return typmap, False


def solve_eqs(eqs):
    typsub = {}
    for eq in eqs:
        typsub, ok = unify(eq.lhs, eq.rhs, typsub, eq.node)
        if not ok:
            return typsub, False
    return typsub, True


def substitute_types(module, typsub, src):
    for node in ast.walk(module):
        typ = getattr(node, '_type', None)
        if typ and isinstance(typ, TypeVar):
            node_src = ast.get_source_segment(src,  node)
            if typ.tag in typsub:
                node._type = typsub[typ.tag]
            else:
                report(src, f'Inconsistent type for "{node_src}" [tag: {typ.tag} ] ', node)


def infer_types(ast, src, log=False):
    global g_src, g_unify_error, g_print_err
    g_src = src
    # 1. Assign type variables
    typgen = TypeGenerator(src)
    typgen.visit(ast)
    if typgen.has_error:
        return False, typgen.errmsg
    if log:
        debug.dump_vars(src, ast)

    # 2. Generate Type Equations
    eqs = EqGenerator(ast).generate()
    if log:
        debug.dump_eqs(src, eqs)

    # 3. Use unification to derive the types [TODO]
    typsub, ok = solve_eqs(eqs)
    if not ok:
        return False, g_unify_error 

    if log:
        print('\n--- Substitutions ---\n')
        for k in typsub.keys():
            print('$'+k[1:], '→', typsub[k])

    substitute_types(ast, typsub, src)
    return True, None


if __name__ == '__main__':
    src = textwrap.dedent("""
        a = 1
        b = a
        b = b + 1
    """)

    infer_types(ast.parse(src), src)
