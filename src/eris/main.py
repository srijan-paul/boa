import ast
import driver

src = """
a = 1 
b = 2
c = a + b
print(c)
"""

# print(ast.dump(ast.parse(src)))
print(driver.compile_py(src, True))