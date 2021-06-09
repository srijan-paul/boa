# Dumping internal data structures

import ast


def dump_symtab(ast: ast.Module):
    print('--- Type Variables ---')


def dump_vars(code: str, mod: ast.Module):
    print('-- Type Vars --')
    print('line'.ljust(10) + 'Expression'.ljust(15), 'Type')
    print('-----'.ljust(9), '---------'.ljust(15), '----')
    for node in ast.walk(mod):
        typ = getattr(node, '_type', None)
        if typ:
           src = ast.get_source_segment(code, node) 
           print(f"({node.lineno}, {node.col_offset})".ljust(10) + src.ljust(15), typ)