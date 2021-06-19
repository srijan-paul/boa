class Builtin:
	def __init__(self, name:str, typ=None):
		self.name  = name
		self.typ = typ


builtins = {
	'print': Builtin('print')
}

