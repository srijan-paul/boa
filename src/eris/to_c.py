import ir
import re
from textwrap import dedent
from er_types import TypeNum, TypeBool, TypeStr, TypeInt, TypeFunc
from builtins_ import builtins


def render(fmt: str, vars: dict):
    to_replace = re.findall(r'\$\w+', fmt)
    for word in to_replace:
        name = word[1:]
        assert name in vars, f"Missing name '{name}'"
        fmt = fmt.replace(word, str(vars[name]))

    return fmt


def cvar(id: str):
    return 'x' + str(id)


def builtin_print(args):
    assert len(args) == 1, "Only single argument print is supported"
    arg = args[0]
    typ = arg._type
    if isinstance(typ, TypeNum):
        return 'print_float'


class Coder:
    def __init__(self):
        self.ccode = ''
        self.has_error = False

    def end():
        pass

    def c_typ(self, typ):
        if isinstance(typ, TypeInt):
            return 'int'
        elif isinstance(typ, TypeNum):
            return 'float'

    def cfun_decl(self, func):
        return render('$ret_typ $name($args)', {
            'ret_typ': self.c_typ(func.typ.ret_type),
            'name': func.name,
            'args': 'int a, int b'
        })

    def gen_c(self, module):
        # main
        return  '#include <stdio.h>\n#include <stdlib.h>\n#include "../lib_boa/boa_runtime.h"\n' + self.emit(module.funcs[0])

    def emit(self, ir):
        tag = ir.__class__.__name__
        method_name = 'emit_' + tag
        method = getattr(self, method_name, None)
        if not method:
            print(f'Skipping IR: {tag}')
            return f'{{ ERROR: NO DISPATCH for {tag} }}'

        return method(ir)

    def emit_decls(self, vars):
        return '\n'.join([f'{self.c_typ(vars[i]._type)} {cvar(i)}; /* {vars[i]._text} */' for i in range(0, len(vars))])


    def emit_Seq(self, ir):
        return ';\n'.join([self.visit(cmd) for cmd in ir.cmds]) + ';\n'

    def emit_Stat(self, ir):
        return self.emit(ir.cmd) + ';\n'

    def c_to_dyn(self, v, typ):
        v = self.emit(v)
        if isinstance(typ, TypeNum): return f'bNumber({v})'
        raise Exception("Not implemented")

    def emit_Func(self, func):
        return render(dedent("""
            $decl {
                $var_decls
                $body
                $opt_ret
            }
        """), {
            'decl': self.cfun_decl(func),
            'body': self.emit(func.body),
            'var_decls': self.emit_decls(func.vars),
            'opt_ret': 'return 0;' if func.name == 'main' else '',
        })


    def emit_For(self, stat):
        from_, to, step = stat.from_, stat.to, stat.step
        return render(dedent("""
            for ($var = $start; $var < $to; $var += $step) {
                $body
            }
        """), {
            'var': self.emit(stat.var),
            'start': self.emit(from_),
            'to': self.emit(to),
            'step': self.emit(step),
            'body': self.emit(stat.body)
        })

    def emit_If(self, stat):
        exp  = self.emit(stat.cond)
        body = self.emit(stat.then)
        return dedent(f"""
            if ({exp}) {{
                {body}
            }}        
        """) 

        


    def emit_Call(self, call):
        func = call.func
        if isinstance(func, ir.Builtin):
            builtin = builtins[func.name]
            c_args = []
            for i in range(len(call.args)):
                arg = call.args[i]
                assert isinstance(builtin.typ, TypeFunc)
                typ = builtin.typ.arg_types[i]
            c_args = ', '.join([self.c_to_dyn(arg, typ) for arg in call.args])
            return f'{builtin.cname}({c_args})'
            

        raise Exception("Not implemented calls")


    def emit_Seq(self, seq):
        return render('$cmds', {
            'cmds': '\n'.join([self.emit(cmd) for cmd in seq.cmds])
        })
    
    def emit_LocalVar(self, var):
        return cvar(var.id)

    def emit_Number(self, num):
        return str(num.value)

    def emit_BinOp(self, cmd):
        return f'{self.emit(cmd.left)} {cmd.op} {self.emit(cmd.right)}'

    def emit_Mov(self, mov):
        return render('$dst = $src;', {
            'dst': cvar(mov.dst),
            'src': self.emit(mov.src)
        });
