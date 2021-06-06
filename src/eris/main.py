import ast
from checker import Checker

src = """
x: int = False
"""

tree = ast.parse(src)
print(ast.dump(tree))

checker = Checker(tree, src)
checker.check()
