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
	#Reference: \d is for decimal numbers,
	#[\d']+ matches 1 or more decimal numbers and ticks,
	#\. matches a period,
	#[\d']* matches any number of decimal numbers and ticks
	#(...)? matches the parens 0 or 1 times
	numbers = r"[\d']+(\.[\d']*)?"
	
	#(\\\n)? matches 0 or 1 instances of a
	#backslash followed by a line break
	strings = r'"(.*(\\\n)?)+"'
	
	comment = r'//(?m.*$)'
	
	multicomment = r'/\*(.*\n?)*\*/'
	
	symbols = re.compile(f'{comment}|{multicomment}|{strings}|{numbers}|' \
											+ tp.ALL_SYMBOLS.regex())
	