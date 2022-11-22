from variables import *

class ThreeInstruction:
    def __init__(self, into, left, right, op):
        self.into = into
        self.left = left
        self.right = right
        self.op = op

class ThreeAddressFunction:
    def __init__(self, instructions = [], labels = dict()):
        self.instructions = instructions
        self.labels = labels