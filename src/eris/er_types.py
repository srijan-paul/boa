class Type:
    def __init__(self, tag, is_primitive: bool = False):
        self.tag = tag
        self.is_primitive = is_primitive

    def __str__(self):
        return self.tag


Type.int = Type('int', True)
Type.float = Type('float', True)
Type.str = Type('str', True)
Type.bool = Type('bool', True)
Type.none = Type('none', True)
Type.any = Type('any', True)


Type._error = Type('error', False)

class ConstType(Type):
    def __init__(self, type, val):
        self.tag = 'const'
        self.typ = type
        self.value = val

Type.primitives = { 
    'int': Type.int,
    'float': Type.float,
    'str': Type.str,
    'bool': Type.bool,
    'NoneType': Type.none,
}


def types_consistent(dst: Type, src: Type) -> bool:
    if dst == src:
        return True
    return False