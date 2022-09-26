from tolkien import Token, TYPES

class Node:
	def __init__(self, children = None):
		self.children = children
		if children:
			for child in children:
				assert isinstance(child, Node)
				self.num_terminals += child.num_terminals
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
		return '<' + self.rule + '>'

class Terminal(Node):
	def __init__(self, token):
		if token is None:
			self.num_terminals = 0
		else:
			assert isinstance(token, Token)
			self.num_terminals = 1
		self.token = token
		super().__init__()
		
	def _getname(self):
		if self.token is None:
			return ''
		return self.token.value

class Reduction:
	def __init__(self, *reduction):
		self.reduction = reduction

		for r in reduction:
			assert isinstance(r, (Rule, Reduction, TYPES, str))

	#If the leftmost tokens match this Reduction,
	#returns a list of Nodes corresponding to the
	#pieces of the reduction. i.e.,
	#tokens = [Token('(',...), Token('foo',...), Token('bar',...), Token(')',...)]
	#self.reduction = ['(', rule_for_foobar, ')']
	#returns [Terminal(tokens[0]), rule_for_foobar.match(tokens[1:3], Terminal(tokens[3])]
	def reduce(self, tokens):
		
		#We match the empty token (i.e., epsilon)
		if len(self.reduction) == 0:
			return [Terminal(None)], 0
	
		matches = []
		tokens_consumed = 0
		for r in self.reduction:
			
			try:
				#If this part of the reduction is another Rule
				if isinstance(r, Rule):
					m = r.descend(tokens[tokens_consumed:])
					
					#Need to make sure the Rule actually matched
					if isinstance(m, int):
						# if we backtrack on every rule we shouldn't have consumed any tokens
						#return None, match + tokens_consumed
						return None, tokens_consumed
						
						
					#We consumed some amount of Tokens
					tokens_consumed += m.num_terminals
					matches.append(m)

				elif isinstance(r, Reduction):
					nested_match, nested_tokens_consumed = r.reduce(tokens[tokens_consumed:])
					if nested_match is None:
						return None, tokens_consumed
					matches += nested_match
					tokens_consumed += nested_tokens_consumed
					
				#If this part of the reduction matches a token type or literal value
				elif self._match_terminal(tokens[tokens_consumed], r):
					matches.append(Terminal(tokens[tokens_consumed]))
					tokens_consumed += 1
				
				#No match
				else:
					return None, tokens_consumed
			
			except IndexError:
				return None, tokens_consumed - 1
		
		return matches, tokens_consumed
	
	#Convenience function to match either token types or literal values
	def _match_terminal(self, token, r):
		if isinstance(r, str):
			return token.value == r
		else:
			# else r is an Enum with token typename values
			return token.typename == r.value

class OptionalReduction(Reduction):
	def reduce(self, tokens):
		matches, tokens_consumed = super().reduce(tokens)
		if matches is None:
		       matches, tokens_consumed = [Terminal(None)], 0
		return matches, tokens_consumed

# TODO: need a better way to handle non-matches that doesn't cause infinite recursion
class RepetitionReduction(Reduction):
	def reduce(self, tokens):
		matches = []
		tokens_consumed = 0
		while True:
			iter_matches, iter_tokens_consumed = super().reduce(tokens[tokens_consumed:])
			if iter_matches is None:
				break
			matches += iter_matches
			# bandaid for now
			if iter_tokens_consumed == 0:
				break
			tokens_consumed += iter_tokens_consumed
		if len(matches) == 0:
			return [Terminal(None)], 0
		return matches, tokens_consumed
			
#Simply an ordered list of Reductions, where each reduction is equivalent to an
#alternate form of a grammer rule.  i.e. Rule ::= Reduction0 | Reduction1 ...
#
#Returns either a parse tree containing the derived source code, or an integer
#if no reductions succeeded giving the maximum tokens consumed along a specific
#reduction.
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
	def descend(self, tokens):
		# DEBUG: needed a conditional breakpoint
		if self.name == 'expression':
			pass
		
		max_consumption = 0
		for r in self.reductions:
			reduction, tokens_consumed = r.reduce(tokens)

			if reduction:
				# can Reduction.reduce() return anything non-nil and non-iterable?
				# Ahh.. I see, empty case
				# if not hasattr(reduction, '__iter__'):
				#	reduction = [reduction]
				return Nonterminal(self.name, reduction)
			max_consumption = max(max_consumption, tokens_consumed)
		return max_consumption

def parse(top_rule, tokens, **kwargs):
	result = top_rule.descend(tokens)
	if isinstance(result, int):
		raise BaseException('Invalid syntax at ' + str(tokens[result].line) + ':' + str(tokens[result].col))
	return result
