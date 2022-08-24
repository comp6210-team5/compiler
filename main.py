import argparse
import tokenizer
import typing

parser = argparse.ArgumentParser()

def main(args):
	tokens = tokenizer.tokenize(source, args)
	print(tokens)



if __name__ == "__main__":
	main(parser.parse_args())