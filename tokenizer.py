import argparse
from token import *

def tokenize(source, print_tokens = False):
	reg = re.compile(rf'(({multicomment})|({comment})|({preprocessor})'\
						+ rf'|({literal})|('\
						+ ALL_OPERATORS.regexstring\
						+ rf')|({identifier})|\s+)')
	
	#not tokens
	ignore = re.compile(rf'(({multicomment})|({comment})|({preprocessor})|\s+)')                        
                
                
	while match := reg.search(source, pos):
		pos = match.end()
		if not ignore.fullmatch(match[0]):
			line, col = linecol(source, pos)
			tokens.append(Token(match[0], line, col))
	
	if print_tokens:
		print(token for token in tokens)
	return tokens

# build a look-up table mapping every position in the source code to its line
# and column number, this avoids having to do an O(n) search for each individual
# position that delimits a token at the cost of memory and redundant storage
# (inter-token positions aren't referenced)
#
# this is still just as lazy but not as slow
def linecols(source):
        positions = {}
        i = 0
        for j, line in enumerate(source.split('\n')):
                for k in range(line):
                        positions[i] = (j, k)
                        i += 1
                # n.b. thus far we've omitted the "\n" character as having any
                # position in the source text, yet the count returned from match
                # will include any "\n" characters, causing us to look-up an
                # offset position as we go through the source-text, so include
                # the newline character (or EOF) as the last character on the
                # column
                positions[i] = (j, len(line))
                i += 1
        return positions
                
#for now we will determine line and col
#by lazily reading as-needed
# TODO: to allow for tracking line and column numbers, the only
# regexes that span multiple lines are whitespace and multicomments,
# which can both be handled on a character-by-character basis pretty
# easily without using a regexy
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
