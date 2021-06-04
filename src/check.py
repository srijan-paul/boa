class Checker:
	def __init__(self, ast):
		self.ast = ast
		self.func_stack = []

	def check(self):
		for stat in self.ast.body:
			self.check_stat(stat)

	def check_stat(self, node):
		node_name = node.__class__.__name__
		method_name = 'check_' + node_name.lower()
		method = getattr(Checker, method_name, None)
		if method is None:
			print('skipping node: ', node_name)
			return
		method(self, node)

	def check_functiondef(self, node):
		fname = node.name
		args = node.args
		pass

	def check_return():
		pass

	def check_assign():
		
		pass
