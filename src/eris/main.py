import ast
import driver
import inference

src = """
x = 1
y = 'x'
z = x + y
"""

tree = ast.parse(src)
inference.infer_types(tree, src)