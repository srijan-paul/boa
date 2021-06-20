import ast
import driver

src = """
a = 1 
b = 'x'
"""

# print(ast.dump(ast.parse(src)))
print(driver.compile_py(src, False))