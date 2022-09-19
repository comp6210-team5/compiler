import argparse
from token import *

def tokenize(source, print_tokens = False):
	reg = re.compile(rf'(?P<multicomment>{multicomment})|'+\
			 rf'(?P<comment>{comment})|'+\
			 rf'(?P<preprocessor>{preprocessor})|'+\
			 rf'(?P<literal>{literal})|'+\
			 r'(?P<operator>' + ALL_OPERATORS.regexstring + ')|'+\
			 rf'(?P<identifier>{identifier})|'+\
			 rf'(?P<whitespace>\s+)')

	pos = 0
	last = 0
	tokens = []
	
	# n.b. "match" is apparently a keyword in python 3.10
	while m := reg.search(source, pos):
		start = m.start()
		pos = m.end()
		if start != last:
			line, col = linecol(source, start)
			# TODO: error handling
			raise Exception(f"found something that doesn't look like a token at l:{line} c:{col}:\n"+\
				f"{source[last:start]}")
		last = pos
		
		line, col = linecol(source, pos)
		typename = m.lastgroup
		if typename not in TYPES:
			raise Exception(f"matched token with typename {typename},"+\
				"which either means reg has a typo in one of the ?P<typenames>"+\
				"or reg.search() didn't find a match and returned None.")
		# check if an identifier match is exactly a keyword and
		# give it the appropriate type here if so
		if typename == 'identifier' and m[0] in KEYWORDS:
			typename = 'keyword'

		if typename not in IGNORED_TYPES:
		        tokens.append(Token(m[0], typename, line, col))
	
	if print_tokens:
		print('\n'.join(f"{token.typename} l:{token.line} c:{token.col} --- {token}" for token in tokens))
	return tokens


# TODO: make faster
def linecol(source, pos):
	if pos == 0:
		return 0, 1

	lines = source[:pos-1].split('\n')
	line = len(lines) + 1
	col = len(lines[-1]) + 1
	return line, col


