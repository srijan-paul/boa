import unittest
from ..checker import Checker
from ..py_types import Type
import ast


def parse(src: str):
    return ast.parse(src)


def errmsg(src: str):
    checker = Checker()
    checker.check(parse(src), src)
    return checker.error_msg


class CheckerTest(unittest.TestCase):
    def test_binop(self):
        self.assertEqual(errmsg('x = 10 + "10"'),
                         "operator '+' cannot be applied to 'float' and 'str'",
                         "Addition of int to string errors out")


print('[OK] All tests passed!')
