from parser import Rule, Reduction
from token import Token, TYPES

binary = Rule('binary')
binary.reductions = [
	Reduction(TYPES.NUMBER, '+', TYPES.NUMBER),
	Reduction(TYPES.NUMBER, '-', TYPES.NUMBER)
]

expr = Rule('expr')
expr.reductions = [
	Reduction('(', expr, ')'),
	Reduction(binary)
]

#hardcode because token.py is not updated yet
tokens = [Token('(',0,0), Token('1',0,1), Token('-',0,2), Token('2',0,3), Token(')',0,4)]
tokens[1].typename = TYPES.NUMBER
tokens[3].typename = TYPES.NUMBER
print(expr.match(tokens))