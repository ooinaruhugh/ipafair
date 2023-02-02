from typing import Tuple, List, cast

from clingo.core import TruthValue
from clingo.control import Control
from clingo.symbol import Number, Function
from clingo.solving import Model, SolveResult

from clingox.program import Program, ProgramObserver
from clingox.backend import SymbolicBackend

from debug import dump_symbolic_atoms, solve_and_dump_model

undirected = True
incremental = True
k = 3
count = 0
show = True

def on_model(m: Model):
    global count
    count += 1

    if show: print(m)

def load_instance_with_external(ctl: Control, instance: str):
    """
    This method is only used internally. 
    It is meant to read the Vertex-Cover instance and feed it to clingo 
    as external atoms.
    """
    with open(instance, "r", encoding="utf-8") as f:
        parameters = f.readline().strip().split(" ")
        n = int(parameters[0])
        undirected = (parameters[1] == "<->")

        with SymbolicBackend(ctl.backend()) as backend:
            for v in range(1,n+1):
                backend.add_external(Function("vertex", [Number(v)]), TruthValue(True))

            for line in f:
                v, edge_list = line.split("|")
                v = int(v)
                
                edge_list = edge_list.strip()
                edge_list = [int(v) for v in edge_list.split(" ")]
                
                for u in edge_list:
                    backend.add_external(Function("edge", [Number(v), Number(u)]), TruthValue(True))
                    if undirected:
                        backend.add_external(Function("edge", [Number(u), Number(v)]), TruthValue(True))

def load_instance_without_external(ctl: Control, instance: str):
    """
    This method is only used internally. 
    It is meant to read the Vertex-Cover instance and feed it to clingo 
    as external atoms.
    """
    with open(instance, "r", encoding="utf-8") as f:
        parameters = f.readline().strip().split(" ")
        n = int(parameters[0])
        undirected = (parameters[1] == "<->")

        for v in range(1,n+1):
            ctl.add("instance", [], f"vertex({v}).")

        for line in f:
            v, edge_list = line.split("|")
            v = int(v)
            
            edge_list = edge_list.strip()
            edge_list = [int(v) for v in edge_list.split(" ")]
            
            for u in edge_list:
                ctl.add("instance", [], f"edge({v}, {u}).")

def add_vertex(ctl: Control, v: int):
    with SymbolicBackend(ctl.backend()) as backend:
        backend.add_external(Function("vertex", [Number(v)]), TruthValue(True))

    ctl.ground([("add_vertex", [Number(v)])])

def del_vertex(ctl: Control, v: int):
    ctl.release_external(Function("vertex", [Number(v)]))

def add_edge(ctl: Control, v: int, u: int):
    with SymbolicBackend(ctl.backend()) as backend:
        backend.add_external(Function("edge", [Number(v), Number(u)]), TruthValue(True))
        if undirected:
            backend.add_external(Function("edge", [Number(u), Number(v)]), TruthValue(True))

    ctl.ground([("add_edge", [Number(v), Number(u)])])

def del_edge(ctl: Control, v: int, u: int):
    ctl.release_external(Function("edge", [Number(v), Number(u)]))
    if undirected:
        ctl.release_external(Function("edge", [Number(u), Number(v)]))


if __name__ == "__main__":
    ctl = Control(arguments=["--models=0"])
    prg = Program()
    ctl.register_observer(ProgramObserver(prg))
    instance = "asp/instance2.vc"

    if incremental:
        load_instance_with_external(ctl, instance)

        # print("\n === Ground program ===")
        # print(prg)
    else:
        load_instance_without_external(ctl, instance)
        ctl.add("instance", [], "edge(X,Y) :- edge(Y,X).")
        ctl.ground([("instance", [])])

    ctl.load("asp/vertex-cover.lp")
    ctl.add("debug", [], "#show in/1.")
    ctl.ground([("init", [])])

    # print("\n === Ground program ===")
    # print(prg)

    print("\n === Solve the instance ===")
    print(ctl.solve(on_model=on_model))
    print(count)

    print(" === Add an edge === ")
    add_vertex(ctl, 2)
    add_edge(ctl, 1, 2)
    # del_edge(ctl, 5, 9)
    count = 0
    print(ctl.solve(on_model=on_model))
    print(count)

    print("\n === Ground program ===")
    print(prg)

    print(" === Delete that edge === ")
    del_edge(ctl, 1,2)
    count = 0
    print(ctl.solve(on_model=on_model))
    print(count)

    print("\n === Ground program ===")
    print(prg)