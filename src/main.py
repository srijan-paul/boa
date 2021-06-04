import ast
from check import Checker

src = """
a = 12 
b = 12
c = a + b
"""

tree = ast.parse(src)
print(tree.body[0].__class__.__name__)
print(ast.dump(tree))

checker = Checker(tree)
checker.check()