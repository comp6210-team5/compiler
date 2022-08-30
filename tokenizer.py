import argparse
from token import *

def tokenize(source):
	reg = re.compile(rf'({multicomment}|{comment}|{preprocessor}'\
						+ rf'|{string}|{number}|'\
						+ ALL_SYMBOLS.regexstring\
						+ rf'|{identifier}|\s+)')
	
	#not tokens
	ignore = re.compile(rf'({multicomment}|{comment}|{preprocessor}|\s+)')
	
	pos = 0
	tokens = []
	while match := reg.search(source, pos):
		pos = match.end()
		if not ignore.fullmatch(match[0]):
			line, col = linecol(source, pos)
			tokens.append(Token(match[0], line, col))
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

#test code
with open('selectionSort.c', 'r') as file:
	for token in tokenize(file.read()):
		print(token)