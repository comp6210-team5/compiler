import networkx as nx
from variables import *

math_comparisons = {'<', '>', '<=', '>=', '==', '!='}
logic_operators = {'&&', '||', '^'}

class Function:
    def __init__(self, name, tac, ret = None):
        # states = []
        
        # #TODO: generate every register state
        
        # stackless = {var for var in get_stackless_variables(states) if not isinstance(var, Immediate)}
        # self.start_state = RegisterState()
        # self.start_state.assign_several(stackless)
        
        # local_stacked = set(tac.locals).difference(stackless)
        # param_stacked = set(tac.params).difference(stackless)
        # self.stack = StackLayout()
        
        # for var in local_stacked:
            # self.stack.add_local(var)
        
        # push_order = []
        # for var in param_stacked:
            # self.stack.add_param(var)
            # push_order.append(tac.params.index(var))
        # self.pushes = reversed(push_order)
        
        self.stack = StackLayout()
        for var in tac.locals:
            self.stack.add_local(var)
        for var in tac.params:
            self.stack.add_param(var)
        
        self.name = name
        self.code = f'{self.name} PROC\n'
        self.code += f'push ebp\nmov ebp, esp\nsub esp, {self.stack.local.top}\n'
        
        #TODO: assembly for the body of the function
        
        if ret and curr_state[ret] != 'eax':
            #store return value in eax
            self.code += ret.load_to_reg('eax', stack_positions[ret])

        self.code += 'mov esp, ebp\npop ebp\nret {self.stack.param.top - 8}\n'
        self.code += f'{self.name} ENDP\n'
    
    def generate_call(self, params, calling_stack, calling_registers):
        code = ''
        for param in reversed(params):
        # for index in self.pushes:
            # param = params[index]
            code += f'push {addr(param, calling_stack, calling_registers)}\n'
        
        code += self.start_state.assembly(calling_stack, calling_registers)
        code += f'call {self.name}\n'
        return code

def from_3_addr(three, stack, prior_registers):
    if not isinstance(three.into, Variable):
        registers = prior_registers.copy()
        code = ''
        if three.left not in registers:
            registers.lazy_assign(three.left)
            code += registers.assembly(stack, prior_registers)
        code += f'cmp {registers[three.left]}, 0\n'
        code += f'jne {three.into}\n'

    elif three.op == '+':
        code, registers, dest_register, other = prepare_overwrite(three, stack, prior_registers)
        code += f'add {dest_register}, {addr(other, stack, registers)}\n'
        
    elif three.op == '-':
        registers = prior_registers.copy()
        code = ''
        if three.left not in registers:
            registers.lazy_assign(three.left, [three.right])
            code += registers.assembly(stack, prior_registers)
        code += f'sub {registers[three.left]}, {addr(three.right, stack, registers)}\n'
        registers.assign(three.into, registers[three.left], True)
        
    elif three.op == '*':
        code, registers, dest_register, other = prepare_overwrite(three, stack, prior_registers)
        code += f'imul {dest_register}, {addr(other, stack, registers)}\n'
        
    elif three.op == '/':
        registers = prior_registers.copy()
        registers.assign(three.left, 'eax')
        code = registers.assembly(stack, prior_registers)
        code += f'idiv {addr(three.right, stack, registers)}\n'
        registers.assign(three.into, 'eax', True)
    
    elif three.op in math_comparisons:
        registers = prior_registers.copy()
        if three.left in registers:
            code = f'cmp {registers[three.left]}, {addr(three.right, stack, registers)}\n'
        elif three.right in registers and three.left in stack:
            code = f'cmp {stack[three.left]}, {registers[three.right]}\n' 
        else:
            registers.lazy_assign(three.left, [three.right])
            code = registers.assembly(stack, prior_registers)
            code += f'cmp {registers[three.left]}, {addr(three.right, stack, registers)}\n'
        
        code += f'mov {address(three.into, stack, registers)}, 0\n'
        
        if three.op == '==':
            code += 'sete'
        elif three.op == '!=':
            code += 'setne'
        elif three.op == '>':
            code += 'setg'
        elif three.op == '>=':
            code += 'setge'
        elif three.op == '<':
            code += 'setl'
        elif three.op == '<=':
            code += 'setle'
        else:
            assert False
            
        if three.into in registers:
            reg = registers[three.into]
            if reg == 'eax':
                code += ' al\n'
            elif reg == 'ebx':
                code += ' bl\n'
            elif reg == 'ecx':
                code += ' cl\n'
            elif reg == 'edx':
                code += ' dl\n'
            else:
                assert False
        else:
            code += f' {stack[three.into].split('PTR ')[1]}\n'
    
    elif three.op in logic_operators:
        code, registers, dest_register, other = prepare_overwrite(three, stack, prior_registers)
        if three.op == '&&':
            code += f'and {dest_register}, {addr(other, stack, registers)}\n'
        elif three.op == '||':
            code += f'or {dest_register}, {addr(other, stack, registers)}\n'
        elif three.op == '^':
            code += f'xor {dest_register}, {addr(other, stack, registers)}\n'
        else:
            assert False
        
    return code, registers

def addr(var, stack, registers):
    if isinstance(var, Immediate):
        return var
    if var in registers:
        return registers[var]
    return stack[var]

#For instructions that overwrite one of their operands.
#Determines which operand is better to overwrite,
#makes sure it is stored in a register,
#and that it is ready to be safely overwritten.
#The returned register state is set up as if three.into
#were already loaded into the destination register;
#do not generate assembly using RegisterState.assembly().
def prepare_overwrite(three, stack, prior_registers):
    registers = prior_registers.copy()
    
    left_loaded = three.left in registers
    left_imm = isinstance(three.left, Immediate)
    right_loaded = three.right in registers
    right_imm = isinstance(three.right, Immediate)
    
    if left_imm and right_imm:
        if left_loaded:
            dest = three.left
        else:
            dest = three.right
    elif left_imm:
        dest = three.left
    elif right_imm:
        dest = three.right
    elif left_loaded:
        dest = three.left
    else:
        dest = three.right
        
    if dest is three.left:
        other = three.right
    else:
        other = three.left
    
    if dest not in registers:
        registers.lazy_assign(dest, [other])
        code = registers.assembly(stack, prior_registers)
    elif not isinstance(dest, Immediate):
        code = f'mov {stack[dest]}, {registers[dest]}\n'
    
    dest_register = registers[dest]
    registers.assign(three.into, dest_register, True)
    return code, registers, dest_register, other

def get_stackless_variables(states):
    #key views are set-like
    return set().intersection(map(lambda x: x.variables.keys(), states))
