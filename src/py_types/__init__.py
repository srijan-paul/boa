class Type:
    def __init__(self, tag, is_primitive: bool = False):
        self.tag = tag
        self.is_primitive = is_primitive

Type.int = Type('int', True)
Type.float = Type('float', True)
Type.str = Type('str', True)
Type.bool = Type('bool', True)
Type.none = Type('none', True)
Type.any = Type('any', True)


Type._error = Type('error', False)

Type.primitives = { 
    'int': Type.int,
    'float': Type.float,
    'str': Type.str,
    'bool': Type.bool,
    'NoneType': Type.none,
}
