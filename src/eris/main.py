import ast
from inference import infer_types
from to_ir import ToIR

src = """
a = 1
b = 2
c = a + b 
"""

tree = ast.parse(src)
infer_types(tree, src)
irconv = ToIR()
irconv.do(tree)

