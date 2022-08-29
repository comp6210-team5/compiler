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
	
	#[^"] matches any character except "
	#(\\\n)? matches 0 or 1 instances of a
	#backslash followed by a line break
	strings = r'"([^"](\\\n)?)+"'
	
	#.* does not match linebreaks
	comment = r'//.*\n'
	
	#(?m.*)*? matches any characters, including linebreaks,
	#matching a minimal number (so until the first */)
	multicomment = r'/\*(?m.*)*?\*/'
	
	symbols = re.compile(f'{comment}|{multicomment}|{strings}|{numbers}|' \
											+ tp.ALL_SYMBOLS.regex())
	