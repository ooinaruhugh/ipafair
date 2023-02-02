from clingo.control import Control
from clingo.symbol import Number, Function
from clingo.solving import Model
from debug import dump_symbolic_atoms, solve_and_dump_model

ctl = Control()
ctl.load("asp/external.lp")
ctl.ground()

print(" === Initial solve ===")
solve_and_dump_model(ctl)

ctl.assign_external(Function("p", [Number(3)]), True)
ctl.solve()

dump_symbolic_atoms(ctl)

print(" === Solve after assigning external ===")
solve_and_dump_model(ctl)

print(" === Solve after assigning more externals ===")
ctl.ground([("succ", [Number(1)]),("succ", [Number(2)])])
ctl.assign_external(Function("p", [Number(4)]), True)

solve_and_dump_model(ctl)
dump_symbolic_atoms(ctl)

print(" === Trying to falsify ===")
ctl.assign_external(Function("p", [Number(5)]), True)
ctl.assign_external(Function("p", [Number(4)]), False)

solve_and_dump_model(ctl)

print(" === Injecting an external number (I guess) === ")
ctl.ground([
    ("setBound", [Number(4)]),
    ("succ", [Number(3)])
])
ctl.assign_external(Function("p", [Number(6)]), True)

solve_and_dump_model(ctl)
dump_symbolic_atoms(ctl)