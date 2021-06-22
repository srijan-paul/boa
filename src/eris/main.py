import ast
import driver

src = """
a = 1
b = 2
c = 0
if a < b:
	c = a
"""

print(ast.dump(ast.parse(src)))
print(driver.compile_py(src, True))