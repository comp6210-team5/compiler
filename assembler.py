from itertools import groupby
import networkx as nx
from collections import counter

registers = {'eax', 'ebx', 'ecx', 'edx'}

class Variable:
    def __init__(self, name, size, stack_pos):
        self.name = name
        self.size = size
        self.stack_pos = stack_pos
    
    def store_from_reg(self, reg):
        return f'mov [esp + {self.stack_pos}], {reg}\n'
    
    def load_to_reg(self, reg):
        return f'mov {reg}, [esp + {self.stack_pos}]\n'
    
    def move_reg(self, fro, to):
        return f'mov {to}, {fro}\n'

class Parameter(Variable):
    def __init__(self, name, size, stack_pos):
        super().__init__(name, size, stack_pos)
    
    def store_from_reg(self, reg):
        return f'mov [ebp + {self.stack_pos} + 8], {reg}\n'
    
    def load_to_reg(self, reg):
        return f'mov {reg}, [ebp + {self.stack_pos} + 8]\n'

class Temporary:
    def __init__(self, value):
        self.value = value
        assert isinstance(self.value, int)
    
    def store_from_reg(self, reg):
        return ''
    
    def load_to_reg(self, reg):
        return f'mov {reg}, {self.value}\n'

class RegisterState:
    def __init__(self, priors = []):
        self.registers = {r: None for r in registers}
        self.variables = dict()
    
    def get_empty_register(self, options = registers):
        for option in options:
            if self.registers[option] is None:
                return self.registers[option]
        return None
    
    def assign(self, variable, register, overwrite = False):
        if self.registers[register] is not None:
            assert overwrite #debug
            del self.variables[self.registers[register]]        
        self.registers[register] = variable
        self.variables[variable] = register
    
    def assign_several(self, variables, reg_options = registers):
        options = set(reg_options)
        needs_assigning = []
        for var in variables:
            needs_assigning.append(var)
            
            if var in self.variables and self.variables[var] in options:
                #already loaded into a valid register
                options.remove(self.variables[var])
                needs_assigning.pop()
                    
        assert len(options) <= len(needs_assigning) #TODO: report
        for var, reg in zip(needs_assigning, options):
            self.assign(var, reg, True)
    
    def assembly(self, prior = None):
        code = ''
        if prior is None:
            #naively load all from memory
            for reg, var in self.registers:
                code += var.load_to_reg(reg)
            
        else:
            #determine what to do with old variables
            moves = []
            for var, reg in prior.variables:
                if var not in self.variables:
                    #store variables if they should no longer be loaded
                    code += var.store_from_reg(reg)
                    
                elif self.variables[var] != reg:
                    #variable needs to be moved to a different register
                    moves.append((reg, self.variables[var]))
            
            if moves:
                # :^)
                g = nx.DiGraph()
                g.add_edges_from(moves)
                for n in g.nodes:
                    assert g.in_degree(n) <= 1 and g.out_degree(n) <= 1 and \ #debug
                           g.in_degree(n) + g.out_degree(n) > 0

                while g.number_of_nodes() != 0:
                    leaves = [n for n in g.nodes if g.out_degree(n) == 0]
                    if leaves:
                        for leaf in leaves:
                            predecessor = next(g.predecessors(leaf))
                            code += f'mov {leaf}, {predecessor}'
                            g.remove_node(leaf)
                            
                    else:
                        #the remaining graph is a single cycle, C_i
                        #I will not be taking requests for a proof at this time
                        n = next(iter(g.nodes))
                        successor = next(g.successors(n))
                        while n is not successor:
                            predecessor = next(g.predecessors(n))
                            code += f'xchg {n}, {predecessor}'
                            n = predecessor
                        break
            
            #now all old variables are where they need to be
            #load new variables from memory
            for var, reg in self.variables:
                if var not in prior.variables:
                    code += var.load_to_reg(reg)
                    
        return code

    def __getitem__(self, reg_or_var):
        if reg_or_var in self.variables:
            return self.variables[reg_or_var]
        if reg_or_var in self.registers:
            return self.registers[reg_or_var]
        return None

class Function:
    def __init__(self, name, three_address, ret = None, params = [], variables = []):
        self.ret = ret
        self.params = params
        self.variables = sorted(variables, key=lambda x:x.stack_pos)
        stack_size = sum([v.size for v in variables])
        
        self.code = f'{name} PROC\n'
        self.code += f'push ebp\nmov ebp, esp\nsub esp, {stack_size}\n'
        
        
        #TODO: assembly for the body of the function
        
        
        self.code += 'mov esp, ebp\npop ebp\nret\n'
        self.code += f'{name} ENDP\n'
        
        self.call_asm = f'CALL {name}\n'