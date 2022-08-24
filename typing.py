#for definitions, classes, and functions
#that all or most other files will import


#simple wrapper to avoid case-sensitivity
#and help ensure everything is read-only
class CaseInsensitiveSet:
	class NotFoundException(Exception):
		def __init__(self, item):
			super().__init__(str(item) + " not found")
	
	def __init__(self, names):
		self._SET = frozenset({name.upper() for name in names})
	
	def __contains__(self, item):
		return item.upper() in self._SET
	
	def __iter__(self):
		for name in self._SET:
			yield name

TYPES = CaseInsensitiveSet({
		'ID',
		'NUMBER',
		'STRING',
		'KEYWORD',
		'CONTROL'
	})
	
KEYWORDS = CaseInsensitiveSet({
	'IF',
	'ELSE',
	'RETURN',
	'SWITCH',
	'CASE',
	'BREAK'
})

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
