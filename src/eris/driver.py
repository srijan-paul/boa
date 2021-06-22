from inference import infer_types
from to_ir import ToIR
from to_c import Coder
from ast import parse

def compile_py(src, debug=False, stop_after='coder'):
    tree = parse(src)
    ok = infer_types(tree, src, debug)
    if not ok: return None
    if stop_after == 'infer':
        return tree

    irconv = ToIR()
    irconv.do(tree, src)

    if irconv.has_error: return None
    if stop_after == 'ir':
        return irconv.module 
    assert stop_after == 'coder', "Stop after must belong to (infer, ir, coder)"

    coder = Coder()
    c = coder.gen_c(irconv.module)
    if coder.has_error: return None
    return c
    
