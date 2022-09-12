from token import Token, TYPES

class Node:
	def __init__(self, children = None):
		self.children = children
		if children:
			for child in children:
				self.num_terminals += child.num_terminals
				assert isinstance(child, Node)
			assert isinstance(self, Nonterminal)
		else:
			assert isinstance(self, Terminal)
	
	def __str__(self):
		return self._to_string(0)
	
	def _to_string(self, depth):
		string = '|' * depth
		string = string + self._getname() + '\n'
		if self.children:
			for child in self.children:
				string = string + child._to_string(depth + 1)
		return string
	
class Nonterminal(Node):
	def __init__(self, rule, children = None):
		self.num_terminals = 0
		super().__init__(children)
		self.rule = rule
		assert isinstance(rule, str)
	
	def _getname(self):
		return self.rule

class Terminal(Node):
	def __init__(self, token):
		self.num_terminals = 1
		super().__init__()
		self.token = token
		assert isinstance(token, Token)
		
	def _getname(self):
		return self.token.value

class Reduction:
	def __init__(self, *reduction):
		self.reduction = reduction
		
		assert len(reduction) > 0
		for r in reduction:
			assert isinstance(r, (Rule, TYPES, str))
		
	#If the leftmost tokens match this Reduction,
	#returns a list of Nodes corresponding to the
	#pieces of the reduction. i.e.,
	#tokens = [Token('(',...), Token('foo',...), Token('bar',...), Token(')',...)]
	#self.reduction = ['(', rule_for_foobar, ')']
	#returns [Terminal(tokens[0]), rule_for_foobar.match(tokens[1:3], Terminal(tokens[3])]
	def reduce(self, tokens):
		matches = []
		tokens_consumed = 0
		for r in self.reduction:
			if isinstance(r, Rule):
				match = r.match(tokens[tokens_consumed:])
				if match is None:
					return None
				tokens_consumed += match.num_terminals
				matches.append(match)
				
			elif self._match_terminal(tokens[tokens_consumed], r):
				matches.append(Terminal(tokens[tokens_consumed]))
				tokens_consumed += 1
			
			else:
				return None
		
		return matches
	
	def _match_terminal(self, token, r):
		if isinstance(r, str):
			return token.value == r
		else:
			return token.typename == r

#Simply an ordered list of Reductions.
#Equivalent to a line of standard grammar.
class Rule:
	name: str
	reductions: list
	
	#We cannot conveniently init the reductions
	#because many Reductions will recursively refer
	#to their containing Rule -- you then need to
	#instantiate the Rule object before its Reductions
	def __init__(self, name):
		self.name = name
		self.reductions = []
	
	#If the leftmost tokens match any of the Reductions,
	#returns a Nonterminal node with corresponding to this Rule
	#and with children corresponding to the matching Reduction.
	def match(self, tokens):
		for r in self.reductions:
			if reduction := r.reduce(tokens):
				return Nonterminal(self.name, reduction)
		return None