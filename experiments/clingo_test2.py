from clingo.control import Control
from clingo.solving import Model

from clingox.program import Program, ProgramObserver, Remapping

model_count = 0
def on_model(m: Model):
    global model_count

    model_count += 1
    print(m)

### Setting up the control object with filter
# ctl = Control()
ctl = Control(arguments=["--models=0"])

prg = Program()
ctl.register_observer(ProgramObserver(prg))

### First load the instance, so we can get the symbolic atoms
ctl.load("asp/vc-instance2.lp")

ctl.ground()
symbols = list(ctl.symbolic_atoms)

ctl.load("asp/vertex-cover.lp")
# ctl.add("minimal", [], "not in(Y) :- edge(X,Y), in(X).")

prog_blocks = [
    ("base", []),
    ("init", []),
    ("instance",[]),
    # ("minimal", []),
]

ctl.ground(prog_blocks)

# print(" === Symbolic atoms ===")
# for x in ctl.symbolic_atoms: 
#     print(x.symbol, x.literal)

# for x in symbols: print(x.literal, x.symbol)

assumptions = []

ctl.load("asp/filter.lp")
print(prg)
print(" === Solve the instance ===")
model_count = 0
print(ctl.solve(assumptions, on_model=on_model))
print(model_count)