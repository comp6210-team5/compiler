import argparse
import re
import typing as tp

class Token:
	def __init__(self, text, line, col):
		self.value = text
		self.line = line
		self.col = col
		self.typename = tp.typename(text)

def tokenize(source, args):
	#\d+ matches 1 or more decimal numbers,
	#[\d']* matches 0 or more decimal numbers and ticks
	decimals = r"\d+[\d']*"
	
	#\.{decimals})? matches 0 or 1 instances of a
	#period followed by more decimals
	numbers = rf'{decimals}(\.{decimals})?'
	
	#[^"]* matches any characters except "
	#(\\\n)? matches 0 or 1 instances of a
	#backslash followed by a line break
	strings = r'"([^"]*(\\\n)?)+"'
	
	#.* does not match linebreaks
	comment = r'//.*\n'
	
	#(?m.*)*? matches any characters, including linebreaks,
	#matching a minimal number (so until the first */)
	multicomment = r'/\*(?m.*)*?\*/'
	
	reg = re.compile(rf'{multicomment}|{comment}|{strings}|{numbers}|' \
									+ tp.ALL_SYMBOLS.regex()) + r'|\n'
	
	pos = 0
	tokens = []
	while match := re.search(source, pos):
		pos = match.end()
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