from logic import *

bob = Symbol("Bob")
alice = Symbol("Alice")
rain = Symbol("Rain")
sunday = Symbol("Sunday")

a = Symbol("A")
b = Symbol("B")

exprs = [And(bob, alice, Not(rain)),
         Implication(And(bob, alice), rain),
         And(Or(bob, alice, Not(And(rain, bob))), sunday),
         Biconditional(Or(Not(a), b), Implication(a, b))]

for i, expr in enumerate(exprs):
    print(f"Expr {i+1}:")
    print(expr)
    print(repr(expr), end="\n\n")

model = {
    "P": True,
    "Q": True
}

p = Symbol("P")
q = Symbol("Q")

# Modus ponens

expr = Implication(And(p, Implication(p, q)), q)
print(expr)
print(expr.eval(model))

# Modul tollens

expr = Implication(And(Not(q), Implication(p, q)), Not(p))
print(expr)
print(expr.eval(model))
