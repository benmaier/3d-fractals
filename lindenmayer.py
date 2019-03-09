class L_system():

    def __init__(self,axiom,production_rules,w=1.):
        self.axiom = axiom
        self.rules = production_rules
        self.stochastic = w<1.
        self.w = w
        self.current_word = self.axiom
        self.n = 0
        
    def get_iteration(self,n=None):
        word = self.current_word

        if n is None:
            n=1
            word = self.current_word
        else:
            word = self.axiom

        for i in range(n):
            new_word = ""
            for letter in word:
                if letter in self.rules:
                    if (not self.stochastic) or (self.stochastic and np.random.random()<self.w):
                        new_word += self.rules[letter]
                    else:
                        new_word += letter
                else:
                    new_word += letter
            word = str(new_word)

        self.current_word = word
        self.n = i
        return word
            
    def draw(self,n=None):
        pass


