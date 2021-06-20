from er_types import *

class Builtin:
	def __init__(self, name:str, cname: str, typ=None):
		self.name  = name
		self.cname = cname
		self.typ = typ


builtins = {
	'print': Builtin('print', 'boa_print', TypeFunc([TypeNum()], TypeNone()))
}

