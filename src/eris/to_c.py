import ir
import re
from textwrap import dedent
from er_types import *


def render(fmt: str, vars: dict):
    to_replace = re.findall(r'\$\w+', fmt)
    for word in to_replace:
        name = word[1:]
        assert name in vars, f"Missing name '{name}'"
        fmt = fmt.replace(word, str(vars[name]))

    return fmt


def cvar(id: str):
    return 'x' + str(id)

class Coder:
    def __init__(self):
        self.ccode = ''

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
        return self.emit(module.funcs[0])

    def emit(self, ir):
        tag = ir.__class__.__name__
        method_name = 'emit_' + tag
        method = getattr(self, method_name, None)
        if not method:
            print(f'Skipping IR: {tag}')
            return '{{ ERROR: NO DISPATCH }}'

        return method(ir)

    def emit_decls(self, vars):
        return '\n'.join([f'{self.c_typ(vars[i]._type)} {cvar(i)};' for i in range(0, len(vars))])

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
