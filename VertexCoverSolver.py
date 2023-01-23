import random
from typing import Tuple, List

from clingo.control import Control
from clingo.symbol import Number, Function
from clingo.solving import Model

from debug import dump_symbolic_atoms, solve_and_dump_model

class VertexCoverSolver:
    '''
    A simple, incremental Vertex-Cover solver using clingo.
    It follows the structure of IPAFAIR, an incremental API for AF solvers.
    '''
    def __init__(self, instance: str, k = 3):
        self.undirected = True
        self.ctl = Control()
        
        self.ctl.load("asp/buss-kernel.lp")
        self.load_instance_with_external(instance)

        # self.ctl.add("debug", [], "#show in/1. #show out/1. #show kernel/1. #show low/1. #show next_to_kernel/1. #show test/1.")

        self.ctl.ground([
            ("buss", [Number(k)])
        ])

    def load_instance_with_external(self, instance: str):
        def add_vertex(v: int):
            self.ctl.ground([("add_vertex_pre_ground", [Number(v)])])
            self.ctl.assign_external(Function("vertex", [Number(v)]), True)
        
        def add_edge(v: int, u: int):
            self.ctl.ground([("add_edge_pre_ground", [Number(v), Number(u)])])
            self.ctl.assign_external(Function("edge", [Number(v), Number(u)]), True)
            if self.undirected:
                self.ctl.ground([("add_edge_pre_ground", [Number(u), Number(v)])])
                self.ctl.assign_external(Function("edge", [Number(u), Number(v)]), True)

        with open(instance, "r", encoding="utf-8") as f:
            parameters = f.readline().strip().split(" ")
            n = int(parameters[0])
            self.undirected = (parameters[1] == "<->")

            for v in range(1,n+1):
                add_vertex(v)

            for line in f:
                v, edge_list = line.split("|")
                v = int(v)
                
                edge_list = edge_list.strip()
                edge_list = [int(v) for v in edge_list.split(" ")]
                
                for u in edge_list:
                    add_edge(v, u)

    def add_vertex(self, v: int):
        if Function("vertex", [Number(v)]) in self.ctl.symbolic_atoms:
            self.ctl.assign_external(Function("vertex", [Number(v)]), True)
        else:
            self.ctl.ground([("add_vertex", [Number(v)])])
            self.ctl.assign_external(Function("vertex", [Number(v)]), True)

    def add_edge(self, v: int, u: int):
        self.ctl.ground([("add_edge", [Number(v), Number(u)])])
        self.ctl.assign_external(Function("edge", [Number(v), Number(u)]), True)
        if self.undirected:
            self.ctl.ground([("add_edge", [Number(u), Number(v)])])
            self.ctl.assign_external(Function("edge", [Number(u), Number(v)]), True)

    def del_vertex(self, v: int):
        if Function("vertex", [Number(v)]) in self.ctl.symbolic_atoms:
            self.ctl.assign_external(Function("vertex", [Number(v)]), False)

        edges = [x.symbol for x in vc.ctl.symbolic_atoms.by_signature("edge", 2) if (x.symbol.arguments[0] == Number(v))]

        for x in edges: print(x)
        for e in edges:
            self.del_edge(e.arguments[0].number, e.arguments[1].number)

    def del_edge(self, v: int, u: int):
        if Function("edge", [Number(v), Number(u)]) in self.ctl.symbolic_atoms:
            self.ctl.assign_external(Function("edge", [Number(v), Number(u)]), False)

            if self.undirected:
                self.ctl.assign_external(Function("edge", [Number(u), Number(v)]), False)

    
    def solve(self, assumptions: List[int] = []) -> bool:
        def on_model(m: Model):
            print(m)

        return self.ctl.solve(assumptions, on_model=on_model)

    def extract_witness(self) -> List[int]:
        raise NotImplementedError

if __name__ == "__main__":
    vc = VertexCoverSolver("asp/instance1.vc")
    # vc = VertexCoverSolver("asp/vc-instance2.lp")

    print(" === Solve the instance ===")
    vc.solve()

    print(vc.undirected)

    print(" === Delete a vertex === ")
    vc.del_vertex(1)
    print(vc.solve())
    