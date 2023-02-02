from clingo.control import Control
from clingo.solving import Model

def dump_symbolic_atoms(ctl: Control):
    print(" === Symbolic atoms ===")
    for x in ctl.symbolic_atoms:
        print(x.symbol)

def solve_and_dump_model(ctl: Control):
    def on_model(m: Model):
        print(m)
        
    print(ctl.solve(on_model=on_model))