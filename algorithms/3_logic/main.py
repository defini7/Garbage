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

p = Symbol("P")
q = Symbol("Q")

def check_entailement(*premises, query):
    knowledge = And(*premises)

    result = "✓" if knowledge.entails(query) else "✘"

    print(f"{Implication(knowledge, query)} {result}")

# Modus ponens
check_entailement(p, Implication(p, q), query=q)

# Modul tollens
check_entailement(Not(q), Implication(p, q), query=Not(p))

# Not an entailement
check_entailement(Or(p, q), query=And(p, q))
