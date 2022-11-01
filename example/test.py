from solver import NaiveSolver as AFSolver
import os

path = os.path.dirname(os.path.abspath(__file__))
s = AFSolver("CO", os.path.join(path, "test.apx"))
assert(s.solve_cred(["a"]))
assert(not s.solve_cred(["b"]))

s.del_attack(("a", "b"))
assert(s.solve_cred(["a"]))
assert(s.solve_cred(["b"]))

s.add_argument("c")
s.add_attack(("c", "b"))
s.add_attack(("b", "a"))
assert(s.solve_cred(["a"]))
assert(not s.solve_cred(["b"]))
assert(s.solve_cred(["c"]))

s.del_argument("a")
s.add_argument("d")
s.add_attack(("d", "c"))
s.add_attack(("c", "d"))
assert(s.solve_cred(["b"]))
assert(s.solve_cred(["c"]))
assert(not s.solve_skept(["d"]))
