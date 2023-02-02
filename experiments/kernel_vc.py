from clingo.control import Control
from clingo.symbol import Number
from clingo.solving import Model

def on_model(m: Model):
    print(m)

k = 3

### Setting up the control object with filter
# ctl = Control()
ctl = Control(arguments=["--models=0"])

### First load the instance, so we can get the symbolic atoms
ctl.load("asp/vc-instance2.lp")

ctl.ground()
symbols = list(ctl.symbolic_atoms)

ctl.load("asp/buss-kernel.lp")
# ctl.add("minimal", [], "not in(Y) :- edge(X,Y), in(X).")
ctl.add("instance", [], "edge(X,Y) :- edge(Y,X).")

prog_blocks = [
    ("base", []),
    ("buss", [Number(k)]),
    ("instance",[]),
    # ("minimal", []),
]

ctl.ground(prog_blocks)

print(" === Symbolic atoms ===")
for x in ctl.symbolic_atoms: 
    print(x.symbol, x.literal)


ctl.add("meta", [], "#show high_deg/1. #show test/1. #show out/1.")
assumptions = []
print(" === Solve the instance ===")
print(ctl.solve(assumptions, on_model=on_model))
