import ast
import driver
import inference

src = """
def fun(a, b):
	return a + b
"""

tree = ast.parse(src)
print(ast.dump(tree))
