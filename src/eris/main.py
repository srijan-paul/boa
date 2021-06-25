import ast
import driver
import inference

src = """
z = 'mystr'
x = 's'
"""

tree = ast.parse(src)
print(driver.compile_py(src))
