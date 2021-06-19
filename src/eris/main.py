import ast
import driver

src = """
a = 1
b = 2
print(a + b)
"""

print(driver.compile_py(src))