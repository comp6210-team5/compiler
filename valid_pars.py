from tokenize import *
from tolkien import *


#Function that checks if parentheses are valid

def valid_pars(s: str) -> bool:
    stack = []
    opening = set('([{')
    closing = set(')]}')
    pair = {')' : '(' , ']' : '[' , '}' : '{'}
    for i in range(len(s)):
        if s[i] in opening :
            stack.append(i)
        if s[i] in closing :
            if not stack :
                return False
            elif s[stack.pop()] != pair[s[i]] :
                return False
            else :
                continue
    if not stack :
        return True
    else :
        return False
