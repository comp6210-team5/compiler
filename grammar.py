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
assignment_expression = Rule('assignment_expression')
# same

primary_expression = Rule('primary_expression')
primary_expression.reductions += [
    Reduction(TYPES.IDENTIFIER),
    Reduction(TYPES.LITERAL),
    Reduction('(', expression, ')'),
]

postfix_tail = Rule('postfix_tail')
postfix_tail.reductions += [
    Reduction('[', expression, ']'),
    Reduction('(',
              OptionalReduction(assignment_expression,
                                RepetitionReduction(',', assignment_expression)),
              ')'),
    Reduction('++'),
    Reduction('--'),
]
              
postfix_expression = Rule('postfix_expression')
postfix_expression.reductions += [
    Reduction(primary_expression, RepetitionReduction(postfix_tail)),
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

multiplicative_tail = Rule('multiplicative_tail')
multiplicative_tail.reductions += [
    Reduction('*', unary_expression),
    Reduction('/', unary_expression),
    Reduction('%', unary_expression),
]

multiplicative_expression = Rule('multiplicative_expression')
multiplicative_expression.reductions += [
    Reduction(unary_expression, RepetitionReduction(multiplicative_tail)),
]

additive_tail = Rule('additive_tail')
additive_tail.reductions += [
    Reduction('+', multiplicative_expression),
    Reduction('-', multiplicative_expression),
]

additive_expression = Rule('additive_expression')
additive_expression.reductions += [
    Reduction(multiplicative_expression, RepetitionReduction(additive_tail)),
]

shift_tail = Rule('shift_tail')
shift_tail.reductions += [
    Reduction('<<', additive_expression),
    Reduction('>>', additive_expression),
]

shift_expression = Rule('shift_expression')
shift_expression.reductions += [
    Reduction(additive_expression, RepetitionReduction(shift_tail)),
]

relational_tail = Rule('relational_tail')
relational_tail.reductions += [
    Reduction('<', shift_expression),
    Reduction('>', shift_expression),
    Reduction('<=', shift_expression),
    Reduction('>=', shift_expression),
]

relational_expression = Rule('relational_expression')
relational_expression.reductions += [
    Reduction(shift_expression, RepetitionReduction(relational_tail)),
]

equality_tail = Rule('equality_tail')
equality_tail.reductions += [
    Reduction('==', relational_expression),
    Reduction('!=', relational_expression),
]

equality_expression = Rule('equality_expression')
equality_expression.reductions += [
    Reduction(relational_expression, RepetitionReduction(equality_tail)),
]

and_tail = Rule('and_tail')
and_tail.reductions += [
    Reduction('&', equality_expression),
]

and_expression = Rule('and_expression')
and_expression.reductions += [
    Reduction(equality_expression, RepetitionReduction(and_tail)),
]

xor_tail = Rule('xor_tail')
xor_tail.reductions += [
    Reduction('^', and_expression),
]

xor_expression = Rule('xor_expression')
xor_expression.reductions += [
    Reduction(and_expression, RepetitionReduction(xor_tail)),
]

or_tail = Rule('or_tail')
or_tail.reductions += [
    Reduction('|', xor_expression),
]

or_expression = Rule('or_expression')
or_expression.reductions += [
    Reduction(xor_expression, RepetitionReduction(or_tail)),
]

logical_and_tail = Rule('logical_and_tail')
logical_and_tail.reductions += [
    Reduction('&&', or_expression),
]

logical_and_expression = Rule('logical_and_expression')
logical_and_expression.reductions += [
    Reduction(or_expression, RepetitionReduction(logical_and_tail)),
]

logical_or_tail = Rule('logical_or_tail')
logical_or_tail.reductions += [
    Reduction('||', logical_and_expression),
]

logical_or_expression = Rule('logical_or_expression')
logical_or_expression.reductions += [
    Reduction(logical_and_expression, RepetitionReduction(logical_or_tail)),
]

assignment_op = Rule('assignment_op')
assignment_op.reductions += [
    Reduction('='),
    Reduction('*='),
    Reduction('/='),
    Reduction('%='),
    Reduction('+='),
    Reduction('-='),
    Reduction('<<='),
    Reduction('>>='),
    Reduction('&='),
    Reduction('^='),
    Reduction('|='),
]

assignment_expression.reductions += [
    Reduction(logical_or_expression),
    Reduction(unary_expression, assignment_op, assignment_expression),
]

expression.reductions += [
    Reduction(assignment_expression, RepetitionReduction(',', assignment_expression)),
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


