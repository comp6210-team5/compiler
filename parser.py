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
		self.choices = None
		
	# needs to be initialized after all of the reductions have been added
	def _initChoices(self):
		self.choices = [0 for _ in range(len(self.reduction))]
		for i, r in enumerate(self.reduction):
			assert isinstance(r, (Rule, Reduction, TYPES, str))
			if isinstance(r, Rule):
				# We assume all rules have at least one
				# reduction. A rule matching an empty string may
				# have a single, empty reduction.
				assert(len(r.reductions) > 0)
				self.choices[i] = len(r.reductions) - 1

	# iterate exhaustively through all potential combinations of reduction
	# choices among each of the rules in the top-level of this reduction
	# (any nested reductions should handle their own iterative exhaustions
	# using this as well)
	def iterChoices(self, skip):
		c = self.choices[skip:]
		i = [0 for _ in range(len(c))]
		yield i
		while not all([j == k for j, k in zip(i, c)]):
			j = len(c) - 1
			i[j] = (i[j] + 1) % (c[j] + 1)
			while i[j] == 0:
				j -= 1
				i[j] = (i[j] + 1) % (c[j] + 1)
			yield i

	# Returns a generator over all possible reduction matches under all
	# possible derivation choices of any rules within the reduction.  The
	# generator iterates over tuples of:
	# (0) lists of Nodes corresponding to individually matched rules,
	# reductions, or terminals contained within this Reduction.
	# and 
	# (1) the number of terminals consumed to produce (err.. reduce?)
	# the match.
	# if skip is > 0, then skip the first 'skip' parts of the reduction
	def reduce(self, tokens, skip=0):
		# We assume reduce will only be called on a reduction at a point
		# once the grammar is finalized (where all rules in the
		# reduction have been both instantiated and filled with
		# reductions.
		if self.choices is None:
			self._initChoices()
			
		#We match the empty token (i.e., epsilon)
		if len(self.reduction[skip:]) == 0:
			# TODO: does yield behave the same way as return, in
			# that anything below this statement isn't executed if
			# true? Does yielding a single element like this yield
			# it only once, and is exhausted for following
			# iterations? Or will it yield this repeatedly?
			yield [Terminal(None)], 0
		else:
			# For every possible choice of reductions of any sub rules (This
			# loop handles iteration over all possible choices of top-level
			# rules contained in this reduction, and repeatedly yields all
			# available matches from any nested reduction or rule which are
			# themselves recursively iterated during a particular step,
			# provided that, for each step of the below iteration the nested
			# iterations of nested rules and reductions start over, which I
			# think is the case.
			for choice_list in self.iterChoices(skip):

				# current index in the token list
				current = 0
				for i, (choice, r) in enumerate(zip(choice_list, self.reduction[skip:])):
					# TODO: do we need to wrap in a try-catch IndexError block?
					if isinstance(r, Rule):
						result = r.descend(tokens[current:], choice)
					# nested reductions can be thought of as rules
					# with a single reduction choice
					elif isinstance(r, Reduction):
						result = r.reduce(tokens[current:])
					elif self._match_terminal(tokens[current], r):
						result = [([Terminal(tokens[current])], 1)]
					else:
						result = []
					# for each match and length of match (in tokens) in the result
					for prefix, len_i in result:
						# TODO: if we skip all of the
						# reductions, does it return an empty
						# match successfully?
						# UPDATE: apparently not?
						if i+1 == len(self.reduction[skip:]):
							yield prefix, len_i
						# TODO: if calling self.reduce() inside
						# of a super.reduce() call from
						# OptionalReduction or
						# RepetitionReduction, does it call the
						# subclass reduction first, as I (the
						# programmer) intend? Or does it call
						# immediately back to super.reduce(),
						# which will cause errors.
						for tail, len_j in self.reduce(tokens[current+len_i:], i+1):
							yield prefix + tail, len_i + len_j
						
	
	#Convenience function to match either token types or literal values
	def _match_terminal(self, token, r):
		if isinstance(r, str):
			return token.value == r
		else:
			# else r is an Enum with token typename values
			return token.typename == r.value

class OptionalReduction(Reduction):
	def reduce(self, tokens, skip=0):
		result = next(super().reduce(tokens, skip), None)
		if result is None:
			yield [Terminal(None), 0]
		else:
			yield result

# TODO: need a better way to handle non-matches that doesn't cause infinite recursion
class RepetitionReduction(Reduction):
	def reduce(self, tokens, skip=0):
		matches = []
		tokens_consumed = 0
		while True:
			result = next(super().reduce(tokens[tokens_consumed:], skip), None)
			if result is None:
				break
			matches_i, length_i = result

			matches += matches_i
			# NOTE: ensure that the empty string is not matched
			# inside a RepetitionReduction otherwise we'll keep
			# matching that without consuming tokens
			assert(length_i > 0)
			tokens_consumed += length_i
		if len(matches) == 0:
			yield [Terminal(None)], 0
		else:
			yield matches, tokens_consumed
			
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
	def descend(self, tokens, choice):
		if self.name == 'assignment_expression':
			pass
		assert(choice < len(self.reductions))
		
		for reduction, length in self.reductions[choice].reduce(tokens):
			yield [Nonterminal(self.name, reduction)], length


def parse(top_rule, tokens, **kwargs):
	# note: top rule must have a single reduction
	assert(len(top_rule.reductions) == 1)
	result = next(top_rule.descend(tokens, 0), None)

	# TODO: add a max_tokens_consumed-type counter to the new logic
	# TODO: the top_rule matches the empty program if something internal
	# fails to parse, therefore it never returns an int. Should revise to
	# fail if there's tokens remaining and we failed to match them all.

	if not result:
		raise BaseException("Invalid syntax at *shrug*")
	
	return result
