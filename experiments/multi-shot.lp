#external p(1;2;3).
p(0) :- p(3).
p(0) :- not p(0).
#program succ(n).
#external p(n+3).
p(n) :- p(n+3).
p(n) :- not p(n+1), not p(n+2).

#script(python)
from clingo import Function, Number
def main(prg):
    prg.ground([("base", [])])
    prg.assign_external(Function("p", [Number(3)]), True)
    prg.solve()
    prg.assign_external(Function("p", [Number(3)]), False)
    prg.solve()
    prg.ground([("succ", [Number(1)]),("succ", [Number(2)])])
    prg.solve()
    prg.ground([("succ", [Number(3)])])
    prg.solve()
#end.
