import unittest
from checker import Checker
from er_types import Type
import ast

def parse(src: str):
    return ast.parse(src)


def silent_error(_, _msg, _node):
    pass

def check(src: str):
    checker = Checker(parse(src), src)
    checker.on_error = silent_error
    checker.check()
    return checker


def errmsg(src: str):
    return check(src).error_msg


class CheckerTest(unittest.TestCase):
    def test_binop(self):
        self.assertEqual(errmsg('x = 10 + "10"'),
                         "operator '+' cannot be applied to 'int' and 'str'",
                         "Addition of int to string errors out")

        self.assertIsNone(errmsg('x = 10.0 + 20.1'), 'Addition of floats with floats')

    def test_var(self):
        checker = check('a = 1; b = "x"; c = a + b;')
        self.assertEqual(checker.error_msg, "operator '+' cannot be applied to 'int' and 'str'", 'Variables')
        


if __name__ == '__main__':
    unittest.main()
