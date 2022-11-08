from parser import Node, Nonterminal, Terminal, ASTNode

# N.B. "ast" also name-conflicts with pdb

# wrap the rule to AST builder lookup and call in one
def to_ast(nonterminal):
    return RULE_TO_AST[nonterminal.rule_name](nonterminal)

# AST builders

# generic AST builder for binary expressions whose nonterminal trees have have
# (eventual) children in an alternating sequence of left-expression, op,
# right-expression as a result of rules of the form <expr> { <op> <expr> }
def _ast_binary_expr(nonterminal):
    return __ast_binary_expr_list(nonterminal.children)

# rather than modify the nonterminal by deleting children, this helper takes a
# children list as argument and recursively builds the tree (left-associatively
# corresponds to starting at the end of the expression tail list)
def __ast_binary_expr_list(nodes):
    assert(len(nodes) > 0)

    if len(nodes) == 1:
        return to_ast(nodes[0])
    else:
        # we have a non-empty repetition of binary expression tails (the <op> <expr> part) to deal with, recursively
        root = to_ast(nodes[-1])
        root.children.insert(0, __ast_binary_expr_list(nodes[:-1]))
        return root

# for a single <expr_tail> rule, return a tree rooted w/ the operator
def _ast_binary_tail(nonterminal):
    # each rule must be <op> <expr>
    assert(len(nonterminal.children) == 2)
    # for rules of this type, the first child should be the operator
    assert(isinstance(nonterminal.children[0], Terminal))

    return ASTNode(name=nonterminal.children[0].token.value,
                   children=[to_ast(nonterminal.children[1])])

def _ast_unary_expr(nonterminal):
    assert(len(nonterminal.children) == 1 or len(nonterminal.children) == 2)

    # if this rule was parsed as a single <postfix_expr>, delegate to its to_ast() 
    if len(nonterminal.children) == 1:
        # TODO: remove a lot of these asserts to avoid setting the grammar in stone,
        # I'm just using them for debug-assisting for initial implementation
        assert(nonterminal.children[0].rule_name == "postfix_expression")
        return to_ast(nonterminal.children[0])

    else:
        # return a tree with the unary op as root and the rest as child
        # TODO: this lacks distinguishing between prefix and postfix "++"
        assert(nonterminal.children[0].rule_name == "unary_op")
        # TODO: here's a good example of where we lose some parsing work
        # (e.g. we have a rule that multiplexes all unary operators and get rid
        # of that distinction by taking only its str() representation in the
        # AST) that could be useful for mapping 3AC instructions based on the
        # specific unary operator
        return ASTNode(name=nonterminal.children[0].children[0].token.value,
                       children=[to_ast(nonterminal.children[1])])
    
def _ast_postfix_expr(nonterminal):
    if len(nonterminal.children) == 1:
        return to_ast(nonterminal.children[0])
    else:
        # TODO: for right now, let's just not support postfix expressions (array
        # indexing, function parameter lists, etc)
        pass

def _ast_primary_expr(nonterminal):
    if len(nonterminal.children) == 1 and nonterminal.children[0].token.typename == "identifier":
        return ASTNode(name="id: " + nonterminal.children[0].token.value)
    elif len(nonterminal.children) == 1:
        return ASTNode(name=nonterminal.children[0].token.value)
    elif len(nonterminal.children) == 3:
        assert(nonterminal.children[0].token.value == '(' and nonterminal.children[2].token.value == ')')
        return to_ast(nonterminal.children[1])
    else:
        assert(len(nonterminal.children) == 1 or len(nonterminal.children) == 3)

def _ast_assignment_expr(nonterminal):
    if len(nonterminal.children) == 1:
        return to_ast(nonterminal.children[0])
    elif len(nonterminal.children) == 3:
        # TODO (1): same as TODO 1 in _ast_unary_expr()
        return ASTNode(name=nonterminal.children[1].children[0].token.value,
                       children=[to_ast(nonterminal.children[0]),
                                 to_ast(nonterminal.children[2])])
    else:
        # TODO: raise some kind of error
        assert(len(nonterminal.children) == 1 or len(nonterminal.children) == 3)

def _ast_expression(nonterminal):
    if len(nonterminal.children) == 1:
        return to_ast(nonterminal.children[0])
    else:
        # TODO: we probably shouldn't support <expr>, <expr>, ... <expr>; 
        return ASTNode(name="<expression sequence>",
                       children=[to_ast(c) for c in nonterminal.children])

def _ast_expression_statement(nonterminal):
    if len(nonterminal.children) == 1:
        assert(nonterminal.children[0].token.value == ';')
        return None

    return to_ast(nonterminal.children[0])

def _ast_compound_statement(nonterminal):
    assert(len(nonterminal.children) >= 2 and nonterminal.children[0].token.value == '{' and nonterminal.children[-1].token.value == '}')
    c = []
    for child in nonterminal.children[1:-1]:
        # declaration AST builders will (I think) return None
        t = to_ast(child)
        if t is not None:
            c.append(t)
    return ASTNode(name="<compound statement>", children=c)

# TODO: do we want to include function declarations in the AST when they're part
# of definitions? Or just use the symbol table to map to a function's
# statement sequence in the AST?
def _ast_function_definition(nonterminal):
    # for now disregard function declarations
    return to_ast(nonterminal.children[1])

# generic function for single nonterminals which may be pruned from the AST
# n.b. also works for single nonterminals with trailing, ignorable stuff
def _ast_nonterminal(nonterminal):
    return to_ast(nonterminal.children[0])

def _ast_program(nonterminal):
    # empty root node to hold everything
    c = []

    for child in nonterminal.children:
        assert(isinstance(child, Nonterminal) and child.rule_name == "top_level_decl")
        t = to_ast(child)
        if t is not None:
            c.append(t)
            
    return ASTNode(name="", children=c)

RULE_TO_AST = {
    "multiplicative_expression" : _ast_binary_expr,
    "multiplicative_tail" : _ast_binary_tail,
    "additive_expression" : _ast_binary_expr,
    "additive_tail" : _ast_binary_tail,
    "shift_expression" : _ast_binary_expr,
    "shift_tail" : _ast_binary_tail,
    "relational_expression" : _ast_binary_expr,
    "relational_tail" : _ast_binary_tail,
    "equality_expression" : _ast_binary_expr,
    "equality_tail" : _ast_binary_tail,
    "and_expression" : _ast_binary_expr,
    "and_tail" : _ast_binary_tail,
    "xor_expression" : _ast_binary_expr,
    "xor_tail" : _ast_binary_tail,
    "or_expression" : _ast_binary_expr,
    "or_tail" : _ast_binary_tail,
    "logical_and_expression" : _ast_binary_expr,
    "logical_and_tail" : _ast_binary_tail,
    "logical_or_expression" : _ast_binary_expr,
    "logical_or_tail" : _ast_binary_tail,
    "unary_expression" : _ast_unary_expr,
    "postfix_expression" : _ast_postfix_expr,
    "primary_expression" : _ast_primary_expr,
    "assignment_expression" : _ast_assignment_expr,
    "expression" : _ast_expression,
    "expression_statement" : _ast_expression_statement,
    "statement" : _ast_nonterminal,
    "compound_statement" : _ast_compound_statement,
    "function_definition" : _ast_function_definition,
    "top_level_decl" : _ast_nonterminal,
    "program" : _ast_program,
}

