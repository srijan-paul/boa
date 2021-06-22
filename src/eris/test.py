from logging import debug
import unittest
from er_types import Type
from inference import infer_types
from textwrap import dedent
import ast


class Assertions:
    def assertInferenceError(self, src: str, expected_err: str, msg: str):
        """Asserts that whenever type inference is run on [src], An error message
        [err] is thrown."""
        tree = ast.parse(src)
        ok, err = infer_types(tree, src)

        if ok or err != expected_err:
          raise AssertionError(msg + f"\nExpected: '{expected_err}'\nGot: '{err}'")


class InferTest(unittest.TestCase, Assertions):
    """Tests for the frontend (Type Generation, Eq Generation and Eq solving)"""

    def test_op_error(self):
        self.assertInferenceError(dedent("""
            x = 1
            y = 'x'
            z = x + y
            """), "Could not unify type 'num' with 'str'", "Integer and String addition raises expected error")


if __name__ == '__main__':
    unittest.main()