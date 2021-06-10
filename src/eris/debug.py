# Dumping internal data structures

import ast


def dump_symtab(ast: ast.Module):
    print('--- Type Variables ---')


def dump_vars(code: str, mod: ast.Module):
    print('\n-- Type Vars --\n')
    print('line'.ljust(10) + 'Expression'.ljust(15), 'Type')
    print('-----'.ljust(9), '---------'.ljust(15), '----')
    for node in ast.walk(mod):
        typ = getattr(node, '_type', None)
        if typ:
           src = ast.get_source_segment(code, node) 
           print(f"({node.lineno}, {node.col_offset})".ljust(10) + src.ljust(15), typ)


def dump_eqs(code: str, eqs: list):
    print('\n--- Equations ---\n')
    for eq in eqs.__reversed__():
        print(eq, f' ( from {ast.get_source_segment(code, eq.node)} )' )