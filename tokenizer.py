import argparse
from token import *

def tokenize(source, print_tokens = False):
	reg = re.compile(rf'(({multicomment})|({comment})|({preprocessor})'\
						+ rf'|({literal})|('\
						+ ALL_OPERATORS.regexstring\
						+ rf')|({identifier})|\s+)')
	
	#not tokens
	ignore = re.compile(rf'(({multicomment})|({comment})|({preprocessor})|\s+)')			    

	pos = 0
	tokens = []
	while match := reg.search(source, pos):
		pos = match.end()
		line, col = linecol(source, pos)
		print(f"l:{line}, c:{col}")
		if not ignore.fullmatch(match[0]):			  
			tokens.append(Token(match[0], line, col))

	
	if print_tokens:
		print('\n'.join(f"{token.typename} l:{token.line} c:{token.col} --- {token}" for token in tokens))
	return tokens

		
#for now we will determine line and col
#by lazily reading as-needed
def linecol(source, pos):
	if pos == 0:
		return 0, 1

	lines = source[:pos-1].split('\n')
	line = len(lines) + 1
	col = len(lines[-1]) + 1
	return line, col


