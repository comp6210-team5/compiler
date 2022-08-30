import argparse
import re
import typing as tp

class Token:
	def __init__(self, text, line, col):
		self.value = text
		self.line = line
		self.col = col
		self.typename = tp.typename(text)
	
	def __str__(self):
		return self.value

def tokenize(source):

        #\d matches 0...9
        #('?\d)* matches 0 or more decimal numbers separated by an optional tick
        decimal_digits = r"\d('?\d)*"
        decimal_lit = rf"\d('?{decimal_digits})?"
        
        hex_digits = r"[0-9a-fA-F]('?[0-9a-fA-F])*"
        hex_lit = rf"0(x|X)'?{hex_digits}"

        binary_digits = r"(0|1)('?(0|1))*"
        binary_lit = rf"0(b|B)'?{binary_digits}"

        octal_digits = r"[0-7]('?[0-7])*"
        octal_lit = rf"0(o|O)'?{octal_digits}"
        
        integer_lit = rf"({decimal_lit})|({hex_lit})|({binary_lit})|({octal_lit})"

        decimal_float_lit = rf"({decimal_digits}\.({decimal_digits})?)|(({decimal_digits})?\.{decimal_digits})"

        escaped_char = r"""\\[abefnrtv\\'"]"""
        hex_byte_value = r"\\x[0-9A-Fa-f]{2}"
        octal_byte_value = r"\\[0-7]{3}"
        byte_value = rf"({hex_byte_value})|({octal_byte_value})"
        printable_ascii = r"""[ !"#$%&'()*+,\-./0-9:;<=>?@A-Z[\\\]^_`a-z{|}~]"""
        ascii_value = rf"({printable_ascii})|({escaped_char})"
        char_lit = rf"'(({ascii_value})|({byte_value}))'"
        
	#[^"]* matches any characters except "
	#(\\\n)? matches 0 or 1 instances of a
	#backslash followed by a line break
	strings = r'"([^"]*(\\\n)?)+"'
	
	#.*? does not match linebreaks, is minimal
	#(?m:$) matches end-of-line
	comment = r'//.*?(?m:$)'
	
	#(?m.*)*? matches any characters, including linebreaks,
	#matching a minimal number (so until the first */)
	multicomment = r'/\*(?m:.*)*?\*/'
	
	#alphabet character or underscore followed by
	#any number of alphanumerics or underscores
	identifier = r'[a-zA-Z_][\w_]*'
	
	reg = re.compile(rf'({multicomment}|{comment}|{strings}|{numbers}|' \
						+ tp.ALL_SYMBOLS.regex() + rf'|{identifier}|\s+)')
	whitespace = re.compile(r'\s+')
	
	pos = 0
	tokens = []
	while match := reg.search(source, pos):
		pos = match.end()
		if not whitespace.fullmatch(match[0]):
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

with open('selectionSort.c', 'r') as file:
	for token in tokenize(file.read()):
		print(token)
