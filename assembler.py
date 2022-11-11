from itertools import groupby

registers = {'EAX', 'EBX', 'ECX', 'EDX'}

class Instruction:
    def __init__(self, priors = []):
        self.priors = priors

class RegisterState:
    def __init__(self, priors = []):
        self.priors = priors
        if len(priors) == 1:
            self.state = priors[0].state.copy()
            self.map = priors[0].map.copy()
        else:
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
    
    def copy(self):
        return RegisterState(self)
    
    def assembly(self):
        if len(self.priors) == 1:
            if self.state == self.priors[0].state and self.map == self.priors[0].map:
                return None
                

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

class Location:
    def __init__(self, size, address = None, register = None):
        self.size = size
        
        assert bool(address) ^ bool(register) #xor
        if address:
            self.location = address
        if register == 'any':
            

class Parameter:
    def __init__(self, name, type, location):
        pass

class Function:
    def __init__(self, name, three_address, ret = None, params = []):
        self.ret = ret
        self.params = params
        
        self.code = f'{name} PROC\n'
        
        #TODO: assembly for the body of the function
        
        self.code += f'{name} ENDP\n'
        
        self.call_asm = f'CALL {name}\n'
        self.ret_asm = None