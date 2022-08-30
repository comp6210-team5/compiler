#this is its own file since presumably other modules will need
#to understand how to use tokens, but not the tokenizer itself

import re

_REGEX_ESCAPES = {
	'(',
	')',
	'|',
	'[',
	']',
	'+',
	'*',
	'$',
	'^',
	'.',
	'?',
	'{',
	'}',
	'\\'
}

class RegexSet:
	def __init__(self, names):
		self._SET = frozenset(names)
		self.regexstring = str()
		for val in sorted(self._SET, key=lambda x: -len(x)):
			for char in val:
				if char in _REGEX_ESCAPES:
					self.regexstring = self.regexstring + '\\'
				self.regexstring = self.regexstring + rf'{char}'
			self.regexstring = self.regexstring + '|'
		self.regexstring = r'(?i:' + self.regexstring[:-1] + r')'
		self.regexcomp = re.compile(self.regexstring)
	
	def __contains__(self, item):
		return item in self._SET
	
	def __iter__(self):
		for name in self._SET:
			yield name
	
	@classmethod
	def union(cls, *others):
		sets = [other._SET for other in others]
		return cls(frozenset.union(*sets))

KEYWORDS = RegexSet({
	'if',
	'else',
	'return',
	'switch',
	'case',
	'while',
	'break',
	'continue'
})

#Segregate operators by length, to make it easy to set precedence in the lexer
ONECHAR_OPERATORS = RegexSet({
	';',
	':',
	'?',
	'+',
	'-',
	'/',
	'*',
	'<',
	'>',
	'=',
	'!',
	'&',
	'|',
	'[',
	']',
	'^',
	'(',
	')',
	',',
	'{',
	'}',
	'.',
	'\\'
})

TWOCHAR_OPERATORS = RegexSet({
	'!=',
	'==',
	'<=',
	'>=',
	'&&',
	'||',
	'++',
	'--'
})

ALL_OPERATORS = RegexSet.union(ONECHAR_OPERATORS, TWOCHAR_OPERATORS)
ALL_SYMBOLS = RegexSet.union(KEYWORDS, ALL_OPERATORS)

TYPES = frozenset({
	'OPERATOR',
	'KEYWORD',
	'STRING',
	'NUMBER',
	'ID'
})

#matches 1 decimal number,
#followed by 0 or more decimal numbers and ticks
decimal = r"[0-9][0-9']*"

hexadecimal = r'0x[0-9a-fA-F]+'

#(\.{decimals})? matches 0 or 1 instances of a
#period followed by more decimals
number = rf'({decimal}(\.{decimal})?|{hexadecimal})'
number_comp = re.compile(number)

#[^"] matches any characters except "
#(\\\n)? matches 0 or 1 instances of a
#backslash followed by a line break
string = r'"(([^"]|\\")*(?m:\\$)?)+"'
string_comp = re.compile(string)

#alphabet character or underscore followed by
#any number of alphanumerics or underscores
identifier = r'[a-zA-Z_][a-zA-Z0-9_]*'
identifier_comp = re.compile(identifier)

#.*? does not match linebreaks, is minimal
#(?m:$) matches end-of-line
comment = r'//.*?(?m:$)'

#(?m.*)*? matches any characters, including linebreaks,
#matching a minimal number (so until the first */)
multicomment = r'/\*(?m:.*)*?\*/'

#not supported yet
preprocessor = r'#.*?(?m:$)'

class Token:
	def __init__(self, text, line, col):
		self.value = text
		self.line = line
		self.col = col
		
		if number_comp.match(text):
			self.typename = 'NUMBER'
		elif string_comp.match(text):
			self.typename = 'STRING'
		elif ALL_OPERATORS.regexcomp.match(text):
			self.typename = 'OPERATOR'
		elif KEYWORDS.regexcomp.match(text):
			self.typename = 'KEYWORD'
		elif identifier_comp.match(text):
			self.typename = 'ID'
		else:
			raise "can't deduce token type"
	
	def __str__(self):
		return self.value