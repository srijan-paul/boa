import ast
from inference import infer_types
from to_ir import ToIR
from to_c import Coder

src = """
a = 1
b = 2
a = a + b 
"""

tree = ast.parse(src)
infer_types(tree, src)
irconv = ToIR()
irconv.do(tree)
c = Coder().gen_c(irconv.module)
print(c)
