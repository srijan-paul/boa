class Type:
	def __init__(self, tag, is_primitive: bool = False):
		self.tag = tag
		self.is_primitive = is_primitive

Type.int = Type('int', True)
Type.str = Type('str', True)
Type.bool = Type('bool', True)
Type.none = Type('none', True)
