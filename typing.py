#for definitions, classes, and functions
#that all or most other files will import

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

#simple wrapper to avoid case-sensitivity
#idk if we'll keep this, we may want case sensitivity
class CaseInsensitiveSet:
	def __init__(self, names):
		self._SET = frozenset({name.upper() for name in names})
		self.onechar = True
		for name in names:
			if len(name) != 1:
				self.onechar = False
				break
	
	def __contains__(self, item):
		return item.upper() in self._SET
	
	def __iter__(self):
		for name in self._SET:
			yield name
	
	
	def regex(self):
		reg = str()
		for val in self._SET:
			if val in _REGEX_ESCAPES:
				reg = reg + '\\'
			reg = reg + rf'{val}|'
		return '(' + reg[:-1] + ')'
	
		
	
	@classmethod
	def union(cls, *others):
		sets = [other._SET for other in others]
		return cls(frozenset.union(*sets))

KEYWORDS = CaseInsensitiveSet({
	'IF',
	'ELSE',
	'RETURN',
	'SWITCH',
	'CASE',
	'WHILE',
	'BREAK',
	'CONTINUE'
})

#Segregate operators by length, to make it easy to set precedence in the lexer
ONECHAR_OPERATORS = CaseInsensitiveSet({
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
	'\\'
})

print(ONECHAR_OPERATORS.regex())

TWOCHAR_OPERATORS = CaseInsensitiveSet({
	'!=',
	'==',
	'<=',
	'>=',
	'&&',
	'||',
	'++',
	'--'
})

ALL_OPERATORS = CaseInsensitiveSet.union(ONECHAR_OPERATORS, TWOCHAR_OPERATORS)

TYPES = CaseInsensitiveSet({
	'OPERATOR',
	'KEYWORD',
	'STRING',
	'NUMBER',
	'ID'
})

def typename(text):
	if text in ALL_OPERATORS:
		return 'OPERATOR'
	elif text in KEYWORDS:
		return 'KEYWORD'
	elif text[0] == '"' and text[-1] == '"':
		return 'STRING'
	elif text.isdigit():
		return 'NUMBER'
	return 'ID'