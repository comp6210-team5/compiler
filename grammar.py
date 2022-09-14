from parser import Rule, Reduction
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
tokens = [Token('(',0,0), Token('(',0,0), Token('1',0,1), Token('-',0,2), Token('2',0,3), Token(')',0,4), Token(')',0,0)]
tokens[2].typename = TYPES.NUMBER
tokens[4].typename = TYPES.NUMBER
print(expr.match(tokens))

del tokens[2:5]
print(expr.match(tokens))