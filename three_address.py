from variables import *

#We support conditional jumps; these are deduced
#by into not being a Variable (rather the label to jump to),
#and take only a single logical value, left.
#If left is nonzero, the jump occurs.
#The actual condition should be a separate instruction,
#storing the result as zero or nonzero as expected.
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
        