from solver import NaiveSolver as AFSolver
import os

path = os.path.dirname(os.path.abspath(__file__))
s = AFSolver("CO", os.path.join(path, "test.af"))
assert(s.solve_cred([1]))
assert(not s.solve_cred([2]))

s.del_attack(1,2)
assert(s.solve_cred([1]))
assert(s.solve_cred([2]))

s.add_argument(3)
s.add_attack(3, 2)
s.add_attack(2, 1)
assert(s.solve_cred([1]))
assert(not s.solve_cred([2]))
assert(s.solve_cred([3]))

s.del_argument(1)
s.add_argument(4)
s.add_attack(4, 3)
s.add_attack(3, 4)
assert(s.solve_cred([2]))
assert(s.solve_cred([3]))
assert(not s.solve_skept([4]))
