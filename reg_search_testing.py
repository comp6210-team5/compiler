# this is a very particular test scenario for some bug we're having with /*
# comments */ causing our lexer to hang. This is to-be-deleted after resolution.
# I'm just writing this in a script because I've been playing around with it in
# an interpreter (because print statements aren't enough and pdb has a naming
# collision with our token.py file

# before running this make sure to download gzip.c from
# https://people.csail.mit.edu/smcc/projects/single-file-programs/gzip.c
with open("gzip.c") as f:
    source = f.read()

# the particular comment of note starts at position 409
print(source[409:450])

# matching this with our multicomment regex is fine
from token import *

# in case we change (fix) the multicomment regex (again):
multicomment = r'/\*(.*|\n)*?\*/'

reg = re.compile(rf'(({multicomment})|({comment})|({preprocessor})'\
		 + rf'|({literal})|('\
		 + ALL_OPERATORS.regexstring\
		 + rf')|({identifier})|\s+)')

# this will print a match
print(reg.search(source[409:450]))

# but try this and it will hang
# reg.search(source[409:])

# adding the following comment is also fine
print(source[409:514])

# this will match... It will match the entire string (both comments), which
# means our lazy matching isn't working
print(reg.search(source[409:514]))

# but a further issue is that, if the comments aren't closed, it just hangs
# print(source[409:513])
# reg.search(source[409:513])


