from tolkien import Token, TYPES
from typing import Callable

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
		
	# Returns a generator over all possible reduction matches under all
	# possible derivation choices of any rules within the reduction.  The
	# generator iterates over tuples of:
	# (0) lists of Nodes corresponding to individually matched rules,
	# reductions, or terminals contained within this Reduction.
	# and 
	# (1) the number of terminals consumed to produce (err.. reduce?)
	# the match.
	#
	# TODO: figure out how to memoize the results of reduce() and descend()
	# on the same token set (first thought is whenever the generator for a
	# particular length of tokens is iterated, also store its results in a
	# list and re-iterate through that list rather than creating any new
	# generators (new calls to descend() or reduce()) for any particular
	# length of tokens.
	def reduce(self, tokens):
			
		#We match the empty token (i.e., epsilon)
		if len(self.reduction) == 0:
			# TODO: does yield behave the same way as return, in
			# that anything below this statement isn't executed if
			# true? Does yielding a single element like this yield
			# it only once, and is exhausted for following
			# iterations? Or will it yield this repeatedly?
			yield [Terminal(None)], 0
		else:
			# Iterate through the parts of the reduction, saving our
			# place every time we come across a rule or nested
			# reduction (which may contain a rule). If we make it
			# through the entire reduction, yield the result. If
			# we've either yielded a result or hit a part that
			# doesn't match (an unmatching terminal, or a rule or
			# nested reduction which returns an exhausted
			# generator), backtrack to the last rule or nested
			# reduction and ratchet its returned generator to take a
			# different path. Continue backtracking until all
			# potential choices were exhausted.
			
			i = 0
			match_state = []
			# current token
			current = 0
			# generator holder
			g = None
			# build a running match (list of Nonterminals,
			# Terminals) as we go, and save our place at any
			# opportunity to backtrack. Since we only append to the
			# match_builder from any point on, we can save the place
			# by saving its current length (and discarding anything
			# beyond that length upon backtracking.
			match_builder = []
			
			while True:
				r = self.reduction[i]

				# TODO: do we need to wrap in a try-catch
				# IndexError block?  Or better yet, rigorously
				# figure out indexing and whether the current
				# token hitting the length of the token list is
				# a fail condition or if we can keep going to
				# match empty rules.
				if isinstance(r, Rule):
					if g is None:
						g = r.descend(tokens[current:])
					
					result = next(g, None)
					if result is None:
						if len(match_state) > 0:
							i, current, mb_len, g = match_state.pop()
							match_builder = match_builder[:mb_len]
							continue
						else:
							break
					else:
						match_state.append((i, current, len(match_builder), g))
						m, m_len = result
						match_builder += m
						current += m_len
						i += 1
						g = None
				
				elif isinstance(r, Reduction):
					if g is None:
						g = r.reduce(tokens[current:])
					result = next(g, None)
					if result is None:
						if len(match_state) > 0:
							i, current, mb_len, g = match_state.pop()
							match_builder = match_builder[:mb_len]
							continue
						else:
							break
					else:
						match_state.append((i, current, len(match_builder), g))
						m, m_len = result
						match_builder += m
						current += m_len
						i += 1
						g = None
						
				elif current < len(tokens) and self._match_terminal(tokens[current], r):
					match_builder.append(Terminal(tokens[current]))
					current += 1
					i += 1
				else:
					if len(match_state) > 0:
						i, current, mb_len, g = match_state.pop()
						match_builder = match_builder[:mb_len]
						continue
					else:
						break

				if i == len(self.reduction):
					yield match_builder, current
					if len(match_state) > 0:
						i, current, mb_len, g = match_state.pop()
						match_builder = match_builder[:mb_len]
						continue
					else:
						break
				
	#Convenience function to match either token types or literal values
	def _match_terminal(self, token, r):
		if isinstance(r, str):
			return token.value == r
		else:
			# else r is an Enum with token typename values
			return token.typename == r.value

class OptionalReduction(Reduction):
	def reduce(self, tokens):
		g = super().reduce(tokens)
		while True:
			result = next(g, None)
			if result is None:
				yield [Terminal(None)], 0
				break
			else:
				yield result

class RepetitionReduction(Reduction):
	def reduce(self, tokens):
		# we have to do the same kind of backtracking in repetitions
		match_builder = []
		match_state = []
		current = 0
		g = None

		while True:
			while current < len(tokens):
				if g is None:
					g = super().reduce(tokens[current:])
				
				result = next(g, None)
				if result is None:
					if len(match_state) > 0:
						current, mb_len, g = match_state.pop()
						match_builder = match_builder[:mb_len]
						continue
					else:
						break
				else:
					match_state.append((current, len(match_builder), g))
					g = None
						
					match_i, len_i = result

					# NOTE: ensure the empty string is not matched
					# inside a repetition
					assert(len_i > 0)

					match_builder += match_i
					current += len_i

					yield match_builder, current
					
			if len(match_builder) == 0:
				yield [Terminal(None)], 0
				break
			else:
				break
			
#Simply an ordered list of Reductions, where each reduction is equivalent to an
#alternate form of a grammer rule.  i.e. Rule ::= Reduction0 | Reduction1 ...
#
#Returns either a parse tree containing the derived source code, or an integer
#if no reductions succeeded giving the maximum tokens consumed along a specific
#reduction.
class Rule:
	name: str
	reductions: list
	# function to_ast(), if not None, takes a Nonterminal corresponding to
	# this rule as input and returns its representation in (as) an abstract
	# syntax tree. The first to_ast() function of the shallowest Nonterminal
	# Node in the tree is the only one called by the AST builder, but
	# sub-nodes' to_ast() method may be called recursively by that.
	to_ast: Callable
	
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
		if self.name == 'top_level_decl':
			pass
		for r in self.reductions:
			for subtree, length in r.reduce(tokens):
				yield [Nonterminal(self.name, subtree)], length


def parse(top_rule, tokens, **kwargs):

	g = top_rule.descend(tokens)
	result = next(g, None)
	# the repetition that is the top rule will return each time it matches a
	# new repetition, so keep doing that until it's matched the whole
	# program or failed.
	while result is not None and result[1] < len(tokens):
		result = next(g, None)

	# TODO: add a max_tokens_consumed-type counter to the new logic
	# TODO: the top_rule matches the empty program if something internal
	# fails to parse, therefore it never returns an int. Should revise to
	# fail if there's tokens remaining and we failed to match them all.

	if result is None:
		raise BaseException("Invalid syntax at *shrug*")
	
	return result[0][0]
