import ast


class Type:
    def __init__(self, tag, is_primitive: bool = False):
        self.tag = tag
        self.is_primitive = is_primitive

    def __str__(self):
        return self.tag 

    def __repr__(self):
        return self.tag


class TypeInt(Type):
    def __init__(self):
        super().__init__('int', True)

class TypeNum(Type):
    def __init__(self):
        super().__init__('num', True)


class TypeBool(Type):
    def __init__(self):
        super().__init__('bool', True)


class TypeStr(Type):
    def __init__(self):
        super().__init__('str', True)


class TypeVar(Type):
    def __init__(self, n):
        super().__init__('t' + str(n))

    def __str__(self):
        return '$' + self.tag[1:]

    __repr__ = __str__

class TypeFunc(Type):
    def __init__(self, arg_types, ret_type):
        assert isinstance(arg_types, list) and isinstance(ret_type, Type)
        self.arg_types = arg_types
        self.ret_type  = ret_type


    def __str__(self):
        arg_strs = [str(typ) for typ in self.arg_types]
        return f"({','.join(arg_strs)}) -> {str(self.ret_type)} "


    __repr__ = __str__

class TypeAny(Type):
    def __init__(self):
        super().__init__('any')


class TypeError(Type):
    def __init__(self):
        super().__init__('< error >')

class TypeNone(Type):
    def __init__(self):
        super().__init__('None')


class ConstType(Type):
    def __init__(self, type, val):
        self.tag = 'const'
        self.typ = type
        self.value = val
        self.is_primitive = False

Type.primitives = {
    'num': TypeNum,
    'str': TypeStr,
    'bool': TypeBool
}


def types_consistent(dst: Type, src: Type) -> bool:
    if dst == src:
        return True
    return False


class TypeInfo:
    def __init__(self, typ: Type, value=None):
        self.typ = typ
        self.val = value

    @staticmethod
    def err_type():
        return TypeInfo(TypeError())


class Symbol:
    def __init__(self, decl: ast.Name, t_info: TypeInfo):
        self.name = decl.id if decl else '<NameError>'
        self.decl = decl
        self.type_info = t_info
        self.annotation = None


class TypeClass:
    def __init__(self):
        pass
