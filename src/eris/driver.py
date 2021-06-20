from inference import infer_types
from to_ir import ToIR
from to_c import Coder
from ast import parse


def compile_py(src, debug=False):
	tree = parse(src)
	ok = infer_types(tree, src, debug)
	if not ok: return None

	irconv = ToIR()
	irconv.do(tree)

	if irconv.has_error: return None

	coder = Coder()
	c = coder.gen_c(irconv.module)
	if coder.has_error: return None

	return c
	