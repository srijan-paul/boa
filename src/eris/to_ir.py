import ir


class ToIR:
    def __init__(self):
        self.loc_id_of_decl = {} # int -> ast.Name
        self.visited_decls = {} # { ast.Name }
        self.func = ir.Func()

    def add_local(self, decl):
        self.visited_decls.add(decl)
        self.func.vars.append(decl)
        return len(self.func) - 1

    def emit(self, instr):
        self.func.body.cmds.append(instr)

    def do_stat(self, stat):
        method_name = 'do_' + stat.__class__.__name__.lower()
        method = getattr(self, method_name, None)
        if method is None:
            print(f'toIR: skipping {stat.__class__.__name__}')
            return False

        method(self, stat)

    def do_assign(self, stat):
        lhs = stat.targets
        rhs = stat.value
        assert len(lhs) == 1

        # TODO: handle assignments where the RHS is not
        # an identifier
        if lhs in self.visited_decls:
            # assignment to existing variable
            id = self.loc_id_of_decl[lhs]
            self.emit(ir.Mov(id, self.do_exp(rhs)))
        else:
            # declare new variable in the current function's
            # scope
            id = self.add_local(lhs)
            self.loc_id_of_decl[lhs] = id
            self.emit(ir.Mov(id, self.do_exp(rhs)))


    def do_annassign():
        pass

    def do_for():
        pass

    def do_exp():
        pass

    def do_name():
        pass
