# Boa - A static type inference engine for Python 
A type checker for python that is capable of inferring types and performing flow sensitive static analysis.
Boa is also capable of compiling a subset of Python to native code, making it upwards of 50 times faster and suitable for use in low-energy embedded programming environments like microprocessors.

Here is a very basic example that detects a type error before any code is run:

```py
x = 123 + 3.0 / 1.0 # type of x = float
y = 'abc' # type of y = string
bad = x + y # woops!
```

The above code is obviously incorrect, because we're trying to
add a float and a string, but the Python interpreter won't know that until this chunk of code is executed.
With Boa, mistakes like these can be caught easily even before we have any test coverage:

<img src="./media/ss1.png" height=70/>

(All type soundness errors are detected live, as you're writing the code.)

With a trivial example like that, it might seem redundant to have an inference engine point out mistakes that only
a beginner would make. However, when a codebase gets large enough and you've got several functions all over the place
that have certain restrictions on their parameter types, Boa can be a huge benefit.

Boa exists to demonstrate that a level of indirection and transpilation is not always needed (as in the case of Typescript
and flow) to maintain type soundness in a codebase.

Boa also aims to compile a subset of the Python programming language to native machine code.
This would allow seemingly dynamically typed code to be used for embedded programming environments that cannot afford
to run an entire Python interpreter.


## How does it work ?
To perform the flow sensitive type inference, we use a variation of Damas-Hindley-Milner, empowered with concepts like
Typeclasses, traits and dependent types.

For compilation to ASM, we use C as a backend, along with a High level IR.

## References:
1. [Hindley Milner inference by Stephen Diehl](http://dev.stephendiehl.com/fun/006_hindley_milner.html)
2. [Type traits in rust](https://doc.rust-lang.org/book/ch19-03-advanced-traits.html)
3. [Ian Grant - The Hindley Milner Type inference Algorithm](http://steshaw.org/hm/hindley-milner.pdf)

