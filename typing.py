#for definitions, classes, and functions
#that all or most other files will import


#simple wrapper to avoid case-sensitivity
#idk if we'll keep this, we may want case sensitivity
class CaseInsensitiveSet:
	def __init__(self, names):
		self._SET = frozenset({name.upper() for name in names})
	
	def __contains__(self, item):
		return item.upper() in self._SET
	
	def __iter__(self):
		for name in self._SET:
			yield name
	
	def regex(self):
		reg = r'['
		for val in self._SET:
			if val != ']' and val != '\\' and val != '^':
				reg = reg + rf'{val}'
		if ']' in self._SET:
			reg = r'[]' + reg[1:]
		if '\\' in self._SET:
			reg = reg + '\\'
		if '^' in self._SET:
			reg = reg + r'^'
		return reg + r']'
	
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
	']',
	'^'
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