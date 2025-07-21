class Expression:
    def eval(self, _) -> bool:
        """ Evaluates an expression based on the provided model """
        raise Exception("nothing to evaluate")
    
    def __str__(self):
        """ Provides an expression in a human readable way """
        return ""
    
    def __repr__(self):
        """ Provides an expression as it would be in the code """
        return ""
    
    def symbols(self) -> set:
        """ Returns all symbols from this expression """
        return set()
    
    @staticmethod
    def validate(obj):
        if not isinstance(obj, Expression):
            raise Exception(f"{obj} is not an expression")
    
    @staticmethod
    def parenthesize(expr) -> str:
        """ Parenthesizes the expression if it is not already parenthesized """

        Expression.validate(expr)

        s = str(expr)

        if len(s) == 0 or s.isalpha() or isinstance(expr, Not):
            return s
        
        return f"({s})"
    

class Symbol(Expression):
    def __init__(self, name: str):
        # Let's allow only alphanumerical values
        if not name.isalnum():
            raise Exception(f"invalid symbol: {name}")

        self.name = name

    def eval(self, model):
        try:
            return bool(model[self.name])
        except:
            raise Exception(f"can't find {self.name} in the provided model: {model}")

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
    
    def symbols(self):
        return {self.name}
    
class Not(Expression):
    def __init__(self, expr):
        Expression.validate(expr)
        self.operand = expr

    def eval(self, model):
        return not self.operand.eval(model)
    
    def __str__(self):
        return f"¬{Expression.parenthesize(self.operand)}"
    
    def __repr__(self):
        return f"Not({repr(self.operand)})"
    
    def symbols(self):
        return self.operand.symbols()

    
class And(Expression):
    def __init__(self, *conjuncts):
        for c in conjuncts:
            Expression.validate(c)

        self.conjuncts = list(conjuncts)

    def eval(self, model):
        return all(c.eval(model) for c in self.conjuncts)
    
    def __str__(self):
        if len(self.conjuncts) == 1:
            return str(self.conjuncts[0])

        return " ∧ ".join(Expression.parenthesize(c) for c in self.conjuncts)
    
    def __repr__(self):
        args = ", ".join(repr(c) for c in self.conjuncts)
        return f"And({args})"
    
    def symbols(self):
        return set.union(c.symbols() for c in self.conjuncts)
    
    def add(self, expr):
        Expression.validate(expr)
        self.conjuncts.append(expr)

class Or(Expression):
    def __init__(self, *disjuncts):
        for c in disjuncts:
            Expression.validate(c)

        self.disjuncts = list(disjuncts)

    def eval(self, model):
        return any(c.eval(model) for c in self.disjuncts)
    
    def __str__(self):
        if len(self.disjuncts) == 1:
            return str(self.disjuncts[0])

        return " ∨ ".join(Expression.parenthesize(c) for c in self.disjuncts)
    
    def __repr__(self):
        args = ", ".join(repr(c) for c in self.disjuncts)
        return f"Or({args})"
    
    def symbols(self):
        return set.union(c.symbols() for c in self.disjuncts)
    
    def add(self, expr):
        Expression.validate(expr)
        self.disjuncts.append(expr)


class Implication(Expression):
    def __init__(self, antecedent, consequent):
        Expression.validate(antecedent)
        Expression.validate(consequent)

        self.antecedent = antecedent
        self.consequent = consequent

    def eval(self, model):
        left = self.antecedent.eval(model)
        right = self.consequent.eval(model)

        return not left or right
    
    def __str__(self):
        left = Expression.parenthesize(self.antecedent)
        right = Expression.parenthesize(self.consequent)

        return f"{left} ⇒ {right}"
    
    def __repr__(self):
        return f"Implication({repr(self.antecedent)}, {repr(self.consequent)})"
    
    def symbols(self):
        return set.union(self.antecedent.symbols(), self.consequent.symbols())
    

class Biconditional(Expression):
    def __init__(self, left, right):
        Expression.validate(left)
        Expression.validate(right)

        self.left = left
        self.right = right

    def eval(self, model):
        left = self.left.eval(model)
        right = self.right.eval(model)

        return (not left or right) and (not right or left)
    
    def __str__(self):
        left = Expression.parenthesize(self.left)
        right = Expression.parenthesize(self.right)

        return f"{left} ⇔ {right}"
    
    def __repr__(self):
        return f"Biconditional({repr(self.left)}, {repr(self.right)})"
    
    def symbols(self):
        return set.union(self.left.symbols(), self.right.symbols())
