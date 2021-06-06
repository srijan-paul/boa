import ast
from .checker import Checker

src = """
number = 123 + 3.0 / 1.0
string = 'abc'
bad = number + string
"""

tree = ast.parse(src)
# print(ast.dump(tree))

checker = Checker(tree, src)
checker.check()
