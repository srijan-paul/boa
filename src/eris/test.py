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

    def test_annotation(self):
        self.assertEqual(errmsg('x: int = "x"'), "Cannot assign from 'str' to 'int'.",
                         "type annotation in assignment")
        self.assertIsNone(errmsg("x: float = 123.456"), "Annotated decls work as expected")

    def test_for(self):
        self.assertEqual(errmsg("for i in rnge(10, 1, -1): pass"), 
            "Expected 'range'", "For loop iter function must be 'range'")

        self.assertEqual(errmsg("for f.x in range(1, 2): pass"), 
            "Expected variable name", "For loop iterator must be variable")

        self.assertEqual(errmsg("for f in range('1', 2): pass"), 
            "'range' arguments must be numeric", "for iterator fn args check")


if __name__ == '__main__':
    unittest.main()
