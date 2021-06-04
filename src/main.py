import ast
from check import Checker

src = """
a = 'x'
b = 12
"""

tree = ast.parse(src)
print(tree.body[0].__class__.__name__)
print(ast.dump(tree))

checker = Checker(tree)
checker.check()