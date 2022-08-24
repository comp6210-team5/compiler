#for definitions, classes, and functions
#that all or most other files will import


#simple wrapper to avoid case-sensitivity
#and help ensure everything is read-only
class CaseInsensitiveSet:
	def __init__(self, names):
		self._SET = frozenset({name.upper() for name in names})
	
	def __contains__(self, item):
		return item.upper() in self._SET
	
	def __iter__(self):
		for name in self._SET:
			yield name
	
	@classmethod
	def make_union(cls, *others):
		sets = [other._SET for other in others]
		return cls(frozenset.union(*sets))

TYPES = CaseInsensitiveSet({
	'ID',
	'NUMBER',
	'STRING',
	'KEYWORD',
	'OPERATOR'
})
	
KEYWORDS = CaseInsensitiveSet({
	'IF',
	'ELSE',
	'RETURN',
	'SWITCH',
	'CASE',
	'BREAK'
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
	'|'
})

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

ALL_OPERATORS = CaseInsensitiveSet.make_union(ONECHAR_OPERATORS, TWOCHAR_OPERATORS)

#ripped from the re documentation
#kinda wild that this is in there
class Token:
	#type is a global function, why is official documentation endorsing this name???
	#type : str
	
	#We'll just call it typename, I guess?
    typename: str
    value: str
    line: int
    column: int
