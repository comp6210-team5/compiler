import argparse
import re
import typing as tp

class Token:
	def __init__(self, text, line, col):
		self.value = text
		self.line = line
		self.col = col
		self.typename = tp.typename(text)
	
	def __str__(self):
		return self.value

def tokenize(source):

        #\d matches 0...9
        #('?\d)* matches 0 or more decimal numbers separated by an optional tick
        decimal_digits = r"\d('?\d)*"
        decimal_lit = rf"\d('?{decimal_digits})?"
        
        hex_digits = r"[0-9a-fA-F]('?[0-9a-fA-F])*"
        hex_lit = rf"0(x|X)'?{hex_digits}"

        binary_digits = r"(0|1)('?(0|1))*"
        binary_lit = rf"0(b|B)'?{binary_digits}"

        octal_digits = r"[0-7]('?[0-7])*"
        octal_lit = rf"0(o|O)'?{octal_digits}"
        
        integer_lit = rf"({decimal_lit})|({hex_lit})|({binary_lit})|({octal_lit})"

        decimal_float_lit = rf"({decimal_digits}\.({decimal_digits})?)|(({decimal_digits})?\.{decimal_digits})"

        escaped_char = r"""\\[abefnrtv\\'"]"""
        hex_byte_value = r"\\x[0-9A-Fa-f]{2}"
        octal_byte_value = r"\\[0-7]{3}"
        byte_value = rf"({hex_byte_value})|({octal_byte_value})"
        char_ascii = r'[ !"#$%&()*+,\-./0-9:;<=>?@A-Z[\]^_`a-z{|}~]'
        char_ascii_value = rf"({char_ascii})|({escaped_char})"
        char_lit = rf"'(({char_ascii_value})|({byte_value}))'"

        string_ascii = r"[ !'#$%&()*+,\-./0-9:;<=>?@A-Z[\]^_`a-z{|}~]"
        string_ascii_value = rf"({string_ascii})|({escaped_char})"
        string_lit = rf'"(({string_ascii_value})|({byte_value}))*"'

        literal = re.compile(rf"({string_lit})|({char_lit})|({decimal_float_lit})|({integer_lit})")
	#.*? does not match linebreaks, is minimal
	#(?m:$) matches end-of-line
	comment = re.compile(r'//.*?(?m:$)')
	
	#alphabet character or underscore followed by
	#any number of alphanumerics or underscores
	identifier = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')

        # case-insensitive match of any of the given keywords
        keywords = re.compile(r'(?i:if|else|return|switch|case|while|break|continue)')

        ops_punc = re.compile(tp.ALL_OPERATORS.regex())

        whitespace = set([' ', '\t'])
        newline = '\n'
	
	reg = re.compile(rf'({multicomment}|{comment}|{strings}|{numbers}|' \
						+ tp.ALL_SYMBOLS.regex() + rf'|{identifier}|\s+)')
	
	pos = 0
        lineno = 0
        colno = 0
        multicomment = False
	tokens = []
        while pos < len(source):
                # skip newlines (considered whitespace) and adjust line/col counters
                if source[pos] == newline:
                        pos += 1
                        lineno += 1
                        colno = 0
                        continue

                # if inside a multi-line comment, look only for the terminating */
                if multicomment:
                        if source[pos] != '*':
                                pos += 1
                                colno += 1
                                continue
                        else if pos + 1 == len(source):
                                # let this fall-through to error
                                continue
                        else if source[pos+1] != '/':
                                pos += 2
                                colno += 2
                                continue
                        else:
                                pos += 2
                                colno += 2
                                multicomment = False
                                continue
                                
                else:
                        # skip whitespace
                        if source[pos] in whitespace:
                                pos += 1
                                colno += 1
                                continue
                        # check for /* (this won't conflict with '/'
                        # as an operator if it isn't followed by a
                        # start)
                        if source[pos] == '/' and pos + 1 < len(source) and source[pos+1] == '*':
                                multicomment == True
                                pos += 2
                                colno += 2
                                continue
                        # TODO? skip over single-line comments in the same manner rather than using a regex
                        
                        # now we've skipped white-space and multi-line
                        # comments and are looking at the first
                        # character of the next potential token or
                        # single-line comment or invalid

                        # TODO: we must match keywords first, since
                        # keywords are contained within the
                        # identifiers rule, but matching keywords
                        # first means we split identifiers that have
                        # keywords as proper prefixes, which is a bug
                        # I'm not sure how to handle
                        match = keywords.match(source, pos)
                        if match:
                                pos = match.end()
                                colno = match.end()
                                

                        
        if multicomment:
                # TODO: raise an error for EOF-terminated /*

                        
                
                
	while match := reg.search(source, pos):
		pos = match.end()
		if not whitespace.fullmatch(match[0]):
			line, col = linecol(source, pos)
			tokens.append(Token(match[0], line, col))
	return tokens

# build a look-up table mapping every position in the source code to its line
# and column number, this avoids having to do an O(n) search for each individual
# position that delimits a token at the cost of memory and redundant storage
# (inter-token positions aren't referenced)
#
# this is still just as lazy but not as slow
def linecols(source):
        positions = {}
        i = 0
        for j, line in enumerate(source.split('\n')):
                for k in range(line):
                        positions[i] = (j, k)
                        i += 1
                # n.b. thus far we've omitted the "\n" character as having any
                # position in the source text, yet the count returned from match
                # will include any "\n" characters, causing us to look-up an
                # offset position as we go through the source-text, so include
                # the newline character (or EOF) as the last character on the
                # column
                positions[i] = (j, len(line))
                i += 1
        return positions
                
#for now we will determine line and col
#by lazily reading as-needed
# TODO: to allow for tracking line and column numbers, the only
# regexes that span multiple lines are whitespace and multicomments,
# which can both be handled on a character-by-character basis pretty
# easily without using a regexy
def linecol(source, pos):
	if pos == 0:
		return 0, 1

	lines = source[:pos-1].split('\n')
	line = len(lines) + 1
	col = len(lines[-1]) + 1
	return line, col

with open('selectionSort.c', 'r') as file:
	for token in tokenize(file.read()):
		print(token)
