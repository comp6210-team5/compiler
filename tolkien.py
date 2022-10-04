#this is its own file since presumably other modules will need
#to understand how to use tokens, but not the tokenizer itself

import re
from enum import Enum

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
	'%',
	'~',
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
	'--',
        '*=',
        '/=',
        '%=',
        '+=',
        '-=',
        '&=',
        '^=',
        '|=',
}) # TODO: ok to put 3-char operators here?

ALL_OPERATORS = RegexSet.union(ONECHAR_OPERATORS, TWOCHAR_OPERATORS)
ALL_SYMBOLS = RegexSet.union(KEYWORDS, ALL_OPERATORS)

class TYPES(Enum):
	OPERATOR = 'operator'
	KEYWORD = 'keyword'
	LITERAL = 'literal'
	IDENTIFIER = 'identifier'
        

IGNORED_TYPES = frozenset({
	'comment',
	'multicomment',
	'whitespace',
	'preprocessor',
})

ALL_TYPES = frozenset({
	'operator',
	'keyword',
	'literal',
	'identifier',
	'comment',
	'multicomment',
	'whitespace',
	'preprocessor',
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

# escaped_char includes a newline character to allow "multi-line\
# strings"
escaped_char = r"""\\[0abefnrtv\\'"
]"""
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

#alphabet character or underscore followed by
#any number of alphanumerics or underscores
identifier = r'[a-zA-Z_][a-zA-Z0-9_]*'

#.*? does not match linebreaks, is minimal
#(?m:$) matches end-of-line
comment = r'//.*?(?m:$)'

#(?s:.*)*? matches any characters, including linebreaks,
#matching a minimal number (so until the first */)
# fix: ?s is re.DOTALL, which causes dot to match newlines

# fix2: using re.DOTALL appears to avoid the hanging that lazy matching an OR of
# .* and a newline. Also the former regex was incorrect, should be (.|\n)*?
# rather than (.*|\n)*?, which was probably the reason for hanging
multicomment = r'/\*(?s:.*?)\*/'

#not supported yet
preprocessor = r'#.*?(?m:$)'

class Token:
	def __init__(self, text, typename, line, col):
		self.value = text
		self.typename = typename
		self.line = line
		self.col = col
	
	def __str__(self):
		return self.value
