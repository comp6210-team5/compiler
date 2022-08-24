import argparse
import re
import typing as tp

class Token:
	def __init__(self, text, line, col):
		self.value = text
		self.line = line
		self.col = col
		self.typename = tp.typename(text)
		
def tokenize(source, args):
	pass