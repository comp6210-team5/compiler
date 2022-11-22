import networkx as nx
from variables import *

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
            if isinstance(param, Immediate):
                code += f'push {param.value}\n'
            elif param in calling_registers:
                code += f'push {calling_registers[param]}\n'
            else:
                code += f'push {calling_stack[param]}\n'
        
        code += self.start_state.assembly(calling_stack, calling_registers)
        code += f'call {self.name}\n'
        return code

def from_3_address(three, stack, prior_registers):
    if three.op == '+':
        code, registers, dest_register, other = prepare_overwrite(three, stack, prior_registers)
        code += f'add {dest_register}, {address(other, stack, registers)}\n'
        
    elif three.op == '-':
        code, registers, dest_register, other = prepare_overwrite(three, stack, prior_registers)
        code += f'sub {dest_register}, {address(other, stack, registers)}\n'
        
    elif three.op == '*':
        code, registers, dest_register, other = prepare_overwrite(three, stack, prior_registers)
        code += f'imul {dest_register}, {address(other, stack, registers)}\n'
        
    elif three.op == '/':
        registers = prior_registers.copy()
        registers.assign(three.left, 'eax')
        code = registers.assembly(stack, prior_registers)
        code += f'idiv {address(three.right, stack, registers)}\n'
        registers.assign(three.into, 'eax')
        
    return code, registers

def address(var, stack, registers):
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
    used_regs = set()
    if three.left:
        left_loaded = three.left in registers
        if left_loaded:
            left_reg = registers[three.left]
            used_regs.add(left_reg)
        left_imm = isinstance(three.left, Immediate)
    if three.right:
        right_loaded = three.right in registers
        if right_loaded:
            right_reg = registers[three.right]
            used_regs.add(right_reg)
        right_imm = isinstance(three.right, Immediate)
    if three.into:
        into_loaded = three.into in registers
        if into_loaded:
            into_reg = registers[three.into]
            used_regs.add(into_reg)
        assert not isinstance(three.into, Immediate)
    other_regs = all_registers.difference(used_regs)
    
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
        registers.lazy_assign(dest, other_regs)
        code = registers.assembly(stack, prior_registers)
    elif not isinstance(dest, Immediate):
        code = f'mov {stack[dest]}, {registers[dest]}\n'
    
    dest_register = registers[dest]
    registers.assign(three.into, dest_register)
    return code, registers, dest_register, other

def get_stackless_variables(states):
    #key views are set-like
    return set().intersection(map(lambda x: x.variables.keys(), states))
