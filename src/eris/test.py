from logging import debug
import unittest
from inference import infer_types
from textwrap import dedent
from driver import compile_py
import ast


class Assertions:
    def assertInferenceError(self, src: str, expected_err: str, msg: str):
        """Asserts that whenever type inference is run on [src], An error message
        [err] is thrown."""
        tree = ast.parse(src)
        ok, err = infer_types(tree, src)
        if ok or err != expected_err:
            raise AssertionError(msg + f"\nExpected: '{expected_err}'\nGot: '{err}'")

    def assertSuccess(self, src: str, msg: str):
        """Asserts that a program compiles down to IR and codegens successfully"""
        try:
            res = compile_py(src)
            if not res:
                raise AssertionError(msg + "\nFailed to compile test case")
        except AssertionError as err:
            raise err
        except Exception as ex:
            raise AssertionError(f"{msg}\nInternal Compiler Error while compiling source.\n{ex}")


class InferTest(unittest.TestCase, Assertions):
    """Tests for the frontend (Type Generation, Eq Generation and Eq solving)"""

    def test_op_error(self):
        self.assertInferenceError(dedent("""
            x = 1
            y = 'x'
            z = x + y
            """), "Could not unify type 'num' with 'str'", "Integer and String addition raises expected error")

    def test_if(self):
        self.assertSuccess(dedent("""
        a = 1
        b = 2
        c = 0
        if a < 100:
            c = a + b
        """), "If statements with no else blocks compile successfully")

        self.assertInferenceError(dedent("""
        x = 1
        if x:
            x = 10 
        """), "Could not unify type 'bool' with 'num'", "Error when if statement condition is not a boolean")
        
        
    def test_assign_if(self):

        self.assertSuccess(dedent("""
        a=1
        b=2
        c="3"
        """),"Single assignments are checked successfully")

        '''self.assertInferenceError(dedent( """
        a, b,c = 1, 2,"3"
        """), "Only single assignments are supported", "Expect error on multiple assignments")
        '''
    def test_var(self):
        #self.assertInferenceError(dedent("""
        #for  i in [1,2,3,4,5]: 
         #   pass               
        #"""),"only 'range' based for loops are supported right now.")

        self.assertSuccess(dedent("""
        for i in range(1,5):
            pass
            """),"only 'range' based for loops are supported right now.")

    


if __name__ == '__main__':
    unittest.main()
