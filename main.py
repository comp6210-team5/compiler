import argparse
import tokenizer
from grammar import program
from parser import parse
from abstract_syntax_tree import to_ast

# TODO: does someone use a text editor that inserts tabs rather than spaces?
# not a big deal if that's the case, I can change my settings to use tabs, we
# just need to all be on the same page there because python

def main():
	parser = argparse.ArgumentParser(description="Compile a C program. Any C program.")
	# TODO: what was the flag we needed to use to print tokens / intermediate representations?
	parser.add_argument("-t", "--tokens", action="store_true", help="print tokens to stdout after tokenizing", dest="print_tokens")
	parser.add_argument("file", help="a filepath of a (single-file) C program to be compiled")
	parser.add_argument("-p", "--parse-tree", action="store_true", help="print parse tree to stdout after parsing", dest="print_parse_tree")
	parser.add_argument("-a", "--abstract-syntax-tree", action="store_true", help="print abstract syntax tree to stdout after parsing", dest="print_ast")
	
	# parser.parse_args() should exit and print usage if a file is not given
	args = parser.parse_args()

	with open(args.file) as f:
		# read the entire source file
		source = f.read()

		# pass that source text to the tokenizer
		tokens = tokenizer.tokenize(source, args.print_tokens)

		parse_tree = parse(program, tokens)
		abstract_syntax_tree = to_ast(parse_tree)
		if args.print_parse_tree:
			print(parse_tree)
		if args.print_ast:
			print(abstract_syntax_tree)
		
if __name__ == "__main__":
	main()
