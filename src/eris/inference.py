import ast
from er_types import Type, TypeBool, TypeNum, TypeStr, types_consistent, Symbol, TypeInfo, TypeVar
import debug
from error_report import report


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

        # stores types of all identifiers
        self.symtab = {}  # str -> Symbol 

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

        self.symtab[name.id] = typ
        typ._decl = name 

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
        id = node.id
        if id in self.symtab:
            node._type = self.symtab[id]
            return node._type
        self.error(f"Unknown variable '{id}'", node)

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

    def generate(self):
        self.visit(self.ast)
        return self.eqs

    def visit_Module(self, node: ast.Module):
        for stat in node.body:
            self.visit(stat)

    def visit_Name(self, _):
        pass  # Name types are resolved in the type var generation pass

    def visit_Assign(self, node):
        # TODO: handle RHS that isn't a single symbol
        self.visit(node.value)

    def visit_Constant(self, node):
        assert not isinstance(node._type, TypeVar)

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
        print(f'Eq generation, skipping: {classname(node)}')


def unify_var(typvar: Type, typ: Type, typmap: dict):
    assert isinstance(typvar, TypeVar)
    if typvar.tag in typmap:
        return unify(typmap[typvar], typ, typmap)

    typmap[typvar.tag] = typ
    return typmap


def unify(l_type: Type, r_type: Type, typmap: dict):
    if typmap is None:
        return None

    if l_type == r_type:
        return typmap

    if isinstance(l_type, TypeVar):
        return unify_var(l_type, r_type, typmap)
    elif isinstance(r_type, TypeVar):
        return unify_var(r_type, l_type, typmap)


def solve_eqs(eqs):
    typsub = {}
    for eq in eqs:
        unify(eq.lhs, eq.rhs, typsub)
    return typsub


def substitute_types(module, typsub, src):
    for node in ast.walk(module):
        typ = getattr(node, '_type', None)
        if typ and isinstance(typ, TypeVar):
            node_src = ast.get_source_segment(src,  node)
            if typ.tag in typsub:
                node._type = typsub[typ.tag]
            else:
                report(src, f'Inconsistent type for "{node_src}"', node)


def infer_types(ast, src):
    # 1. Assign type variables
    TypeGenerator(src).visit(ast)
    debug.dump_vars(src, ast)

    # 2. Generate Type Equations
    eqs = EqGenerator(ast).generate()
    debug.dump_eqs(src, eqs)

    # 3. Use unification to derive the types [TODO]
    typsub = solve_eqs(eqs)
    print('\n--- Substitutions ---\n')
    for k in typsub.keys():
        print('$'+k[1:], '→', typsub[k])

    substitute_types(ast, typsub, src)


src = """
a = 1
b = a
b = b + 1
"""

infer_types(ast.parse(src), src)
