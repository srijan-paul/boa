import ast
import driver

src = """
a = 1
for i in range(1, 10):
    print(a)
"""

print(ast.dump(ast.parse(src)))
print(driver.compile_py(src))