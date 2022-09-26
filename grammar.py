from parser import Rule, Reduction, OptionalReduction, RepetitionReduction, parse
from parser import Nonterminal
from tolkien import *
from tokenizer import tokenize

pointer = Rule('pointer')
pointer.reductions += [
    Reduction('*', OptionalReduction(pointer)),
]

declarator = Rule('declarator')
declarator.reductions += [
    Reduction(OptionalReduction(pointer), TYPES.IDENTIFIER),
    Reduction(OptionalReduction(pointer), '(', declarator, ')'),
]

# TODO: add initializers to the grammar

# TODO: we could use a better way to define rules that are only a list of
# potential words or operators. I like the idea of using the token-like approach
# rather than defining a huge rule as below. Just these will get unwieldy to
# work with in the long run.
type_specifier = Rule('type_specifier')
type_specifier.reductions += [
    Reduction('void'),
    Reduction('char'),
    Reduction('short'),
    Reduction('int'),
    Reduction('long'),
    Reduction('float'),
    Reduction('double'),
]

expression = Rule('expression')
# reductions added after sub-expression-types below

primary_expression = Rule('primary_expression')
primary_expression.reductions += [
    Reduction(TYPES.IDENTIFIER),
    Reduction(TYPES.LITERAL),
    Reduction('(', expression, ')'),
]

nested_postfix_expression = Rule('nested_postfix_expression')
nested_postfix_expression.reductions += [
    Reduction(primary_expression, nested_postfix_expression),
    Reduction('[', expression, ']'),
    Reduction('++'),
    Reduction('--'),
    Reduction(),
]

postfix_expression = Rule('postfix_expression')
postfix_expression.reductions += [
    Reduction(primary_expression, nested_postfix_expression),
]

unary_op = Rule('unary_op')
unary_op.reductions += [
    Reduction('--'),
    Reduction('++'),
    Reduction('&'),
    Reduction('*'),
    Reduction('+'),
    Reduction('-'),
    Reduction('~'),
    Reduction('!'),
]

unary_expression = Rule('unary_expression')
unary_expression.reductions += [
    Reduction(postfix_expression),
    Reduction(unary_op, unary_expression),
]

nested_multiplicative_expression = Rule('nested_multiplicative_expression')
nested_multiplicative_expression.reductions += [
    Reduction(unary_expression, nested_multiplicative_expression),
    Reduction('*', unary_expression),
    Reduction('/', unary_expression),
    Reduction('%', unary_expression),
    Reduction(),
]

multiplicative_expression = Rule('multiplicative_expression')
multiplicative_expression.reductions += [
    Reduction(unary_expression, nested_multiplicative_expression),
]

# TODO: the grammar has expression generate a possible comma-separated list of
# expressions... is that valid?
expression.reductions += [
    Reduction(multiplicative_expression)
]

expression_statement = Rule('expression_statement')
expression_statement.reductions += [
    Reduction(OptionalReduction(expression), ';'),
]

statement = Rule('statement')
statement.reductions += [
    Reduction(expression_statement)
]

var_decl = Rule('var_decl')
var_decl.reductions += [
    Reduction(type_specifier, declarator, RepetitionReduction(',', declarator), ';'),
]

declaration = Rule('declaration')
declaration.reductions += [
    Reduction(var_decl),
]

compound_statement = Rule('compound_statement')
compound_statement.reductions += [
    Reduction('{', RepetitionReduction(declaration), RepetitionReduction(statement), '}'),
]

parameter_list = Rule('parameter_list')
parameter_list.reductions += [
    Reduction(type_specifier, declarator, RepetitionReduction(',', type_specifier, declarator)),
]

function_decl = Rule('function_decl')
function_decl.reductions += [
    Reduction(type_specifier, declarator, '(', OptionalReduction(parameter_list), ')'),
]

function_definition = Rule('function_definition')
function_definition.reductions += [
    Reduction(function_decl, compound_statement)
]

top_level_decl = Rule('top_level_decl')
top_level_decl.reductions += [
    Reduction(declaration),
    Reduction(function_decl, ';'),
    Reduction(function_definition),
]

program = Rule('program')
program.reductions += [
    Reduction(RepetitionReduction(top_level_decl)),
]

# testing
with open("test.c") as f:
    source = f.read()

tokens = tokenize(source)
print(parse(program, tokens))

