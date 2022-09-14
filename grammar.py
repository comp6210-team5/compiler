from parser import Rule, Reduction, parse
from token import Token, TYPES

eps = Rule('epsilon')
eps.reductions = [Reduction()]

binary = Rule('binary')
binary.reductions = [
	Reduction(TYPES.NUMBER, '+', TYPES.NUMBER),
	Reduction(TYPES.NUMBER, '-', TYPES.NUMBER)
]

expr = Rule('expr')
expr.reductions = [
	Reduction('(', expr, ')'),
	Reduction(binary),
	Reduction(eps)
]

#hardcode because token.py is not updated yet
tokens = [Token('(',0,0), Token('(',0,1), Token('1',1,0), Token('-',1,1), Token('2',1,2), Token(')',2,0), Token(')',2,1)]
tokens[2].typename = TYPES.NUMBER
tokens[4].typename = TYPES.NUMBER
print(parse(expr, tokens))

del tokens[2:5]
print(parse(expr, tokens))

del tokens[-1]
del expr.reductions[2]
print([token.value for token in tokens])
print(parse(expr, tokens))