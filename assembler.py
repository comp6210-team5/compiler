from itertools import groupby

registers = {'EAX', 'EBX', 'ECX', 'EDX'}

class Variable:
    def __init__(self, name, size, stack_pos):
        self.name = name
        self.size = size
        self.stack_pos = stack_pos
    
    def store_from_reg(self, reg):
        return 'mov [esp + {self.stack_pos}], {reg}\n'
    
    def load_to_reg(self, reg):
        return 'mov {reg}, [esp + {self.stack_pos}]\n'
    
    def __eq__(self, other):
        return self.name == other.name

class Parameter(Variable):
    def __init__(self, name, size, stack_pos):
        super().__init__(name, size, stack_pos)
    
    def store_from_reg(self, reg):
        return 'mov [ebp + {self.stack_pos} + 8], {reg}\n'
    
    def load_to_reg(self, reg):
        return 'mov {reg}, [ebp + {self.stack_pos} + 8]\n'

class RegisterState:
    def __init__(self, priors = []):
        self.state = {r: None for r in registers}
        self.map = dict()
    
    def get_empty_register(self, options = registers, force):
        for option in options:
            if self.state[option] is None:
                return self.state[option]
        assert not force, 'Unable to find empty register' #debug
        return None
    
    def assign(self, register, value, overwrite = False):
        if self.state[register] is not None:
            assert overwrite, 'Invalid overwrite' #debug
            del self.map[self.state[register]]        
        self.state[register] = value
        self.map[value] = register
    
    def assembly(self, prior = None):
        code = ''
        if isinstance(prior, RegisterState):
            for r, var in prior.state:
                if var != self.state[r]:
                    code += var.store_from_reg(r)
        for r, var in self.state:
            code += var.load_to_reg(r)
        return code
                
    def __getitem__(self, reg_or_variable):
        if isinstance(reg_or_variable, Variable):
            if reg_or_variable in self.map:
                return self.map[reg_or_variable]
            return None
        else:
            return self.state[reg_or_variable]

class RegisterStates:
    def __init__(self):
        self._states = dict()
    
    def __getitem__(self, instruction):
        if instruction not in self._states:
            prior = instruction.prior
            if isinstance(prior, Instruction):
                #register states MUST be set in order
                assert prior in self._states, 'Prior register state does not exist'
                self._states[instruction] = self._states[prior].copy()
                
            elif prior:
                g = groupby(prior)
                group = next(g)
                if group and not next(g, False):
                    #all prior states were equivalent
                    self._states[instruction] = self._states[group[0]].copy()
                    
                else:
                    #prior states had different register setups -- clear the registers
                    self._states[instruction] = RegisterState()
                
            else:
                self._states[instruction] = RegisterState()
        return self._states[instruction]

class Function:
    def __init__(self, name, three_address, ret = None, params = [], variables = []):
        self.ret = ret
        self.params = params
        self.variables = sorted(variables, key=lambda x:x.stack_pos)
        
        stack_size = 0
        for variable in self.variables:
            stack_size += variable.size
        
        self.code = f'{name} PROC\n'
        self.code += f'push ebp\nmov ebp, esp\nsub esp, {stack_size}\n'
        
        
        #TODO: assembly for the body of the function
        
        
        self.code += 'mov esp, ebp\npop ebp\nret\n'
        self.code += f'{name} ENDP\n'
        
        self.call_asm = f'CALL {name}\n'