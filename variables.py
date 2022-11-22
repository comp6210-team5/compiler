import random

all_registers = {'eax', 'ebx', 'ecx', 'edx'}

class Variable:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        assert self.size in [1, 2, 4]
        
class Immediate:
    def __init__(self, value):
        self.value = value
        assert isinstance(self.value, int)
    
    def __str__(self):
        return str(self.value)

class LocalStackLayout:
    def __init__(self):
        self.stack = dict()
        self.top = 0
    
    def add(self, var):
        self.stack[var] = self.top
        self.top += var.size
    
    def __getitem__(self, var):
        return f'DWORD PTR [esp + {self.stack[var]}]'
    
    def __contains__(self, var):
        return var in self.stack
    
    def copy(self):
        cls = self.__class__
        out = cls.__new__(cls)
        out.stack = self.stack.copy()
        out.top = self.top
        return out

class ParamStackLayout:
    def __init__(self):
        self.stack = dict()
        self.top = 8
    
    def add(self, var):
        self.stack[var] = self.top
        self.top += var.size
    
    def __getitem__(self, var):
        return f'DWORD PTR [ebp + {self.stack[var]}]'
    
    def __contains__(self, var):
        return var in self.stack
    
    def copy(self):
        cls = self.__class__
        out = cls.__new__(cls)
        out.stack = self.stack.copy()
        out.top = self.top
        return out

class StackLayout:
    def __init__(self):
        self.local = LocalStackLayout()
        self.param = ParamStackLayout()
    
    def add_local(self, var):
        self.local.add(var)
    
    def add_param(self, var):
        self.param.add(var)
    
    def __getitem__(self, var):
        if var in self.local:
            return self.local[var]
        if var in self.param:
            return self.param[var]
        assert False #debug
    
    def __contains__(self, var):
        return var in self.local or var in self.param
    
    def copy(self):
        cls = self.__class__
        out = cls.__new__(cls)
        out.local = self.local.copy()
        out.param = self.param.copy()
        return out

class RegisterState:
    def __init__(self):
        self.reg2var = {r: None for r in all_registers}
        self.var2reg = dict()
    
    def assign(self, var, reg, discard = False):
        if var in self.var2reg and self.var2reg[var] != reg:
            #Variable is loaded into a different register
            if self.reg2var[reg] is not None:
                if discard:
                    del self.var2reg[self.reg2var[reg]]
                    self.reg2var[self.var2reg[var]] = None
                    
                else:
                    #Destination register already has a variable;
                    #move it into the register we previously occupied
                    
                    #The variable in the register we are currently in
                    #equals the variable in our destination register
                    self.reg2var[self.var2reg[var]] = self.reg2var[reg]
                    
                    #The register holding the variable in our destination
                    #register equals the register we are currently in
                    self.var2reg[self.reg2var[reg]] = self.var2reg[var]
                    
                    #Jesus help me I've been coding for 12 hours straight
                    #Does Python have 2-way dictionaries? Please?
                    
            else:
                self.reg2var[self.var2reg[var]] = None
            
        elif self.reg2var[reg] is not None:
            #Destination register already has a variable
            if not discard and open := self.get_empty_register(all_registers - {reg}):
                #Move it into an unoccupied register
                
                #The register holding the variable in our
                #destination register equals the open register
                self.var2reg[self.reg2var[reg]] = open
                
                #The variable in the open register equals
                #the variable in our destination register
                self.reg2var[open] = self.reg2var[reg]
                
            else:
                #No free registers, bye buddy
                del self.var2reg[self.reg2var[reg]]
            
        self.reg2var[reg] = var
        self.var2reg[var] = reg
    
    def get_options(self, exclusions):
        options = all_registers
        if exclusions is None:
            return options
        for val in exclusions:
            if val in options:
                options.remove(val)
            elif val in self.var2reg:
                options.remove(self.var2reg[val])
        return options
    
    def get_empty_register(self, exclusions = None):
        for option in self.get_options(exclusions):
            if isinstance(self.reg2var[option], (NoneType, Immediate)):
                return option
        return None
    
    def lazy_assign(self, var, exclusions = None):
        options = self.get_options(exclusions)
        if open := self.get_empty_register(options):
            self.assign(var, open)
        else:
            self.assign(var, random.choice(list(options)))
    
    def assign_several(self, variables, exclusions = None):
        options = self.get_options(exclusions)
        needs_assigning = []
        for var in variables:
            needs_assigning.append(var)
            
            if var in self.var2reg and self.var2reg[var] in options:
                #already loaded into a valid register
                options.remove(self.var2reg[var])
                needs_assigning.pop()
                    
        assert len(options) <= len(needs_assigning) #debug
        for var, reg in zip(needs_assigning, options):
            self.assign(var, reg)
    
    def assembly(self, stack, prior = None):
        code = ''
        if prior is None:
            #naively load all from memory
            for var, reg in self.var2reg:
                code += f'mov {reg}, {stack[var]}\n'
            
        else:
            #determine what to do with old variables
            moves = []
            for var, reg in prior.var2reg:
                if var not in self.var2reg:
                    #store variables if they should no longer be loaded
                    if not isinstance(var, Immediate):
                        code += f'mov {stack[var]}, {reg}\n'
                    
                elif self.var2reg[var] != reg:
                    #variable needs to be moved to a different register
                    moves.append((reg, self.var2reg[var]))
            
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
            for var, reg in self.var2reg:
                if var not in prior.var2reg:
                    if isinstance(var, Immedaite):
                        code += f'mov {reg}, {var.value}\n'
                    else:
                        code += f'mov {reg}, {stack[var]}\n'
                    
        return code

    def __getitem__(self, reg_or_var):
        if reg_or_var in self.var2reg:
            return self.var2reg[reg_or_var]
        return self.reg2var[reg_or_var]
    
    def __contains__(self, reg_or_var):
        return reg_or_var in self.var2reg or \
            (reg_or_var in self.reg2var and self.reg2var[reg_or_var] is not None)
    
    def copy(self):
        cls = self.__class__
        out = cls.__new__(cls)
        out.registers = self.reg2var.copy()
        out.variables = self.var2reg.copy()
        return out