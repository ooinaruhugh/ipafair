import random
from typing import Tuple, List

from clingo.control import Control
from clingo.symbol import Number, Function
from clingo.solving import Model, SolveResult

from debug import dump_symbolic_atoms, solve_and_dump_model

class VertexCoverSolver:
    '''
    A simple, incremental Vertex-Cover solver using clingo.
    It follows the structure of IPAFAIR, an incremental API for AF solvers.
    '''
    def __init__(self, instance: str, k = 3):
        """
        Instanciates a VertexCoverSolver for the specified instance
        and given instance k. This also prepares clingo with the 
        instance and all the rules to calculate a vertex cover by Buss's kernelization.
        
        Parameters
        ----------
        instance
            The path to the Vertex-Cover instance.
        k
            The parameter for the Vertex-Cover size used in
            the initial computation of Buss's kernel.
        """
        self.undirected = True

        def load_instance_with_external(instance: str):
            """
            This method is only used internally. 
            It is meant to read the Vertex-Cover instance and feed it to clingo 
            as external atoms.
            """
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

        self.ctl = Control()
        
        self.ctl.load("asp/buss-kernel.lp")
        load_instance_with_external(instance)

        self.ctl.add("debug", [], "#show in/1. #show out/1. #show kernel/1. #show low/1. #show next_to_kernel/1. #show test/1.")

        self.ctl.ground([
            ("buss", [Number(k)])
        ])

    def add_vertex(self, v: int):
        """
        Adds the vertex v with all necessary atoms and rules.

        If the vertex v is known to clingo (because it has been specified 
        and removed before), then it just toggles that vertex active.

        Parameters
        ----------
        v
            The index of the added vertex.
        """
        if Function("vertex", [Number(v)]) in self.ctl.symbolic_atoms:
            self.ctl.assign_external(Function("vertex", [Number(v)]), True)
        else:
            self.ctl.ground([("add_vertex", [Number(v)])])
            self.ctl.assign_external(Function("vertex", [Number(v)]), True)

    def add_edge(self, v: int, u: int):
        """
        Adds the edge (v,u) with all necessary atoms and rules.

        If the edge (v,u) is already known to clingo (because it has been specified 
        and removed before), then it just toggles that vertex active.

        If the graph has been specified to be undirected, this also adds the 
        edge in the other direction.

        Parameters
        ----------
        v
            The index of the source of the added edge.
        u
            The index of the target of the added edge. 
        """
        self.ctl.ground([("add_edge", [Number(v), Number(u)])])
        self.ctl.assign_external(Function("edge", [Number(v), Number(u)]), True)
        if self.undirected:
            self.ctl.ground([("add_edge", [Number(u), Number(v)])])
            self.ctl.assign_external(Function("edge", [Number(u), Number(v)]), True)

    def del_vertex(self, v: int):
        """
        Removes the vertex v by disabling it.

        If v does not exist yet, then this does nothing.

        Parameters
        ----------
        v
            The index of the deleted vertex.
        """
        if Function("vertex", [Number(v)]) in self.ctl.symbolic_atoms:
            self.ctl.assign_external(Function("vertex", [Number(v)]), False)

        edges = [x.symbol for x in vc.ctl.symbolic_atoms.by_signature("edge", 2) if (x.symbol.arguments[0] == Number(v))]

        for e in edges:
            self.del_edge(e.arguments[0].number, e.arguments[1].number)

    def del_edge(self, v: int, u: int) -> None:
        """
        Removes the edge (v,u) by disabling it.

        If the edge (v,u) does not exist yet, then it this does nothing.

        If the graph has been specified to be undirected, this also disables the 
        edge in the other direction.

        Parameters
        ----------
        v
            The index of the source of the deleted edge.
        u
            The index of the target of the deleted edge. 
        """
        if Function("edge", [Number(v), Number(u)]) in self.ctl.symbolic_atoms:
            self.ctl.assign_external(Function("edge", [Number(v), Number(u)]), False)

            if self.undirected:
                self.ctl.assign_external(Function("edge", [Number(u), Number(v)]), False)

    
    def solve(self, assumptions: List[int] = []) -> bool:
        """
        Solves the current Vertex-Cover instance under the assumption
        that the atoms in assumptions are contained in the solution.
        """
        def on_model(m: Model):
            print(m)

        result = self.ctl.solve(assumptions, on_model=on_model)
        return result.satisfiable == True

    def extract_witness(self) -> List[int]:
        """
        Returns a solution for the current Vertex-Cover instance 
        if the previous call to solve returned True.
        """
        raise NotImplementedError

if __name__ == "__main__":
    vc = VertexCoverSolver("asp/instance1.vc")
    # vc = VertexCoverSolver("asp/vc-instance2.lp")

    print(" === Solve the instance ===")
    vc.solve()

    print(" === Delete a vertex === ")
    vc.del_vertex(1)
    vc.del_vertex(3)
    print(vc.solve())
    
    print(" === Add an edge === ")
    vc.add_edge(2,4)
    print(vc.solve())