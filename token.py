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


#matches 0 or more decimal numbers separated by an optional, single tick
decimal_digits = r"[0-9]('?[0-9])*"
decimal_lit = rf"[0-9]('?{decimal_digits})?"

hex_digits = r"[0-9a-fA-F]('?[0-9a-fA-F])*"
hex_lit = rf"0(x|X)'?{hex_digits}"

binary_digits = r"(0|1)('?(0|1))*"
binary_lit = rf"0(b|B)'?{binary_digits}"

octal_digits = r"[0-7]('?[0-7])*"
octal_lit = rf"0(o|O)'?{octal_digits}"
        
integer_lit = rf"({decimal_lit})|({hex_lit})|({binary_lit})|({octal_lit})"

# matches decimal digits followed by a period followed by optional decimal
# digits, or optional decimal digits followed by a period followed by decimal
# digits.
decimal_float_lit = rf"({decimal_digits}\.({decimal_digits})?)|(({decimal_digits})?\.{decimal_digits})"

# TODO: do we want a number literal to join all of the individual decimal
# literals? Or do we want to join all literals (numbers and strings) into a
# single token type?

escaped_char = r"""\\[abefnrtv\\'"]"""
hex_byte_value = r"\\x[0-9A-Fa-f]{2}"
octal_byte_value = r"\\[0-7]{3}"
byte_value = rf"({hex_byte_value})|({octal_byte_value})"
char_ascii = r'[ !"#$%&()*+,\-./0-9:;<=>?@A-Z[\]^_`a-z{|}~]'
char_ascii_value = rf"({char_ascii})|({escaped_char})"
char_lit = rf"'(({char_ascii_value})|({byte_value}))'"

string_ascii = r"[ !'#$%&()*+,\-./0-9:;<=>?@A-Z[\]^_`a-z{|}~]"
string_ascii_value = rf"({string_ascii})|({escaped_char})"
string_lit = rf'"(({string_ascii_value})|({byte_value}))*"'

# TODO: add backslash new-line support to the string rule above
# q.v. string = r'"(([^"]|\\")*(?m:\\$)?)+"' from previous version

literal = rf"({string_lit})|({char_lit})|({decimal_float_lit})|({integer_lit})"
literal_comp = re.compile(literal)

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

                if literal_comp.fullmatch(text):
                        self.typename = 'LITERAL'
		elif ALL_OPERATORS.regexcomp.fullmatch(text):
			self.typename = 'OPERATOR'
		elif KEYWORDS.regexcomp.fullmatch(text):
			self.typename = 'KEYWORD'
		elif identifier_comp.fullmatch(text):
			self.typename = 'ID'
		else:
			raise "can't deduce token type"
	
	def __str__(self):
		return self.value
