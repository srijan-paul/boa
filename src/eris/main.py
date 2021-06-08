import ast
from checker import Checker

src = """
a = 10
b = '20'
for f in range(a, b):
  print(i)
"""

tree = ast.parse(src)
print(ast.dump(tree))

checker = Checker(tree, src)
checker.check()
