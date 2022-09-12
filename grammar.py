from token import Token, TYPES

class Node:
	def __init__(self, children = None):
		self.children = children
		self.size = 1
		if children:
			for child in children:
				self.size += child.size
				assert isinstance(child, Node)
			assert isinstance(self, Nonterminal)
		else:
			assert isinstance(self, Terminal)
	
class Nonterminal(Node):
	def __init__(self, rule, children = None):
		super().__init__(children)
		self.rule = rule
		assert isinstance(rule, Rule)

class Terminal(Node):
	def __init__(self, token):
		super().__init__()
		self.token = token
		assert isinstance(token, Token)

#
class Reduction:
	def __init__(self, reduction):
		self.reduction = reduction
		self.terminals = []
		for r in range(len(reduction)):
			if isinstance(reduction[r], TYPES, str):
				self.terminals.append(r)
		
		assert isinstance(reduction, list):
		assert len(reduction) > 0
		assert len(terminals) > 0
		for r in reduction:
			assert isinstance(r, Rule, TYPES, str)
		
	#If the leftmost tokens match this Reduction,
	#returns a list of Nodes corresponding to the
	#pieces of the reduction. i.e.,
	#tokens = [Token('(',...), Token('foo',...), Token('bar',...), Token(')',...)]
	#self.reduction = ['(', rule_for_foobar, ')']
	#returns [Terminal(tokens[0]), rule_for_foobar.reduce(tokens[1:3], Terminal(tokens[3])]
	def reduce(self, tokens):
		if 

#Simply an ordered list of Reductions.
#Equivalent to a line of standard grammar.
class Rule:
	def __init__(self, name, reductions):
		self.name = name
		self.reductions = reductions
		
		assert isinstance(name, str)
		assert isinstance(reductions, list)
		assert len(reductions) > 0
		for r in reductions:
			assert isinstance(r, Reduction)
	
	def reduce(self, tokens):
		output = None
		for r in self.reductions:
			if output := r.reduce(tokens):
				break
		if output is not None:
			output = Nonterminal(self, output)
		return output