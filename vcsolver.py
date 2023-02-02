from typing import List, cast

from clingo.core import TruthValue
from clingo.control import Control
from clingo.symbol import Number, Function
from clingo.solving import Model, SolveResult

from clingox.program import Program, ProgramObserver
from clingox.backend import SymbolicBackend

from re import match

from abc import ABC, abstractmethod

class VertexCoverSolver(ABC):
    '''
    A simple, incremental Vertex-Cover solver using clingo.
    It follows the structure of IPAFAIR, an incremental API for AF solvers.
    '''

    @abstractmethod
    def __init__(self, instance: str):
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
    def del_vertex(self, v: int):
        """
        Removes the vertex v by disabling it.

        If v does not exist yet, then this does nothing.

        Parameters
        ----------
        v
            The index of the deleted vertex.
        """
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError
    
    @abstractmethod
    def solve(self, assumptions: List[int] = []) -> bool:
        """
        Solves the current Vertex-Cover instance under the assumption
        that the atoms in assumptions are contained in the solution.
        """
        raise NotImplementedError

    @abstractmethod
    def extract_witness(self) -> List[int]:
        """
        Returns a solution for the current Vertex-Cover instance 
        if the previous call to solve returned True.
        """
        raise NotImplementedError

class BussSolver(VertexCoverSolver):
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
        self.k = k

        def load_instance_with_external(instance: str):
            """
            This method is only used internally. 
            It is meant to read the Vertex-Cover instance and feed it to clingo 
            as external atoms.
            """
            with open(instance, "r", encoding="utf-8") as f:
                parameters = f.readline().strip().split(" ")
                n = int(parameters[0])
                self.undirected = (parameters[1] == "<->")

                with SymbolicBackend(self.ctl.backend()) as backend:
                    for v in range(1,n+1):
                        backend.add_external(Function("vertex", [Number(v)]), TruthValue(True))

                    for line in f:
                        v, edge_list = line.split("|")
                        v = int(v)
                        
                        edge_list = edge_list.strip()
                        edge_list = [int(v) for v in edge_list.split(" ")]
                        
                        for u in edge_list:
                            backend.add_external(Function("edge", [Number(v), Number(u)]), TruthValue(True))
                            if self.undirected:
                                backend.add_external(Function("edge", [Number(u), Number(v)]), TruthValue(True))

        def parse_logic_program_instance(instance: str):
            vertices = []

            with open(instance, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()

                    if match(r"^edge\(.*\)\.", line) or match(r"^vertex\(.*\)\.", line):
                        self.ctl.add("instance", [], "#external " + line)
                    elif match(r"^edge([A-Z]*,[A-Z]*) :- edge([A-Z]*,[A-Z]*).", line):
                        self.undirected = True

                if self.undirected:
                    raise NotImplementedError
                    # self.ctl.ground()

            return vertices
                
        self.ctl = Control(arguments=["--models=0"])
        # self.ctl = Control()

        self.prg = Program()
        self.ctl.register_observer(ProgramObserver(self.prg))
        
        load_instance_with_external(instance)
        # self.ctl.load("asp/incr-vc.lp")
        self.ctl.load("asp/buss-kernel.lp")
        print(" === Grounded program ===")
        print(self.prg)

        # self.ctl.add("debug", [], "#show in/1. #show out/1. #show kernel/1. #show low/1. #show next_to_kernel/1. #show test/1.")
        self.ctl.add("debug", [], "#show in/1.")

        self.ctl.ground([
            # ("init", []),
            ("init", [Number(k)]),
            # ("instance", [])
        ])

        print(" === Grounded program ===")
        print(self.prg)

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

        if not self.undirected:
            edges = [x.symbol for x in vc.ctl.symbolic_atoms.by_signature("edge", 2) if (x.symbol.arguments[1] == Number(v))]
        
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
            self.model_count += 1
            # print(m)

        self.model_count = 0
        result = self.ctl.solve(assumptions, on_model=on_model)

        print(self.model_count)

        return cast(SolveResult, result).satisfiable == True

    def extract_witness(self) -> List[int]:
        """
        Returns a solution for the current Vertex-Cover instance 
        if the previous call to solve returned True.
        """
        raise NotImplementedError

class SimpleVertexCoverSolver(VertexCoverSolver):
    def __init__(self, instance: str = "", incremental = True, debug = False, show_models = False):
        def load_instance_with_external(instance: str):
            """
            This method is only used internally. 
            It is meant to read the Vertex-Cover instance and feed it to clingo 
            as external atoms.
            """
            with open(instance, "r", encoding="utf-8") as f:
                parameters = f.readline().strip().split(" ")
                n = int(parameters[0])
                self.undirected = (parameters[1] == "<->")

                with SymbolicBackend(self.ctl.backend()) as backend:
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

        def load_instance_without_external(instance: str):
            """
            This method is only used internally. 
            It is meant to read the Vertex-Cover instance and feed it to clingo 
            as external atoms.
            """
            with open(instance, "r", encoding="utf-8") as f:
                parameters = f.readline().strip().split(" ")
                n = int(parameters[0])
                self.undirected = (parameters[1] == "<->")

                for v in range(1,n+1):
                    self.ctl.add("instance", [], f"vertex({v}).")

                for line in f:
                    v, edge_list = line.split("|")
                    v = int(v)
                    
                    edge_list = edge_list.strip()
                    edge_list = [int(v) for v in edge_list.split(" ")]
                    
                    for u in edge_list:
                        self.ctl.add("instance", [], f"edge({v}, {u}).")

        self.ctl = Control(arguments=["--models=0"])
        self.prg = Program()
        self.ctl.register_observer(ProgramObserver(self.prg))

        self.debug = debug
        self.show_models = show_models
        self.undirected = True

        if instance:
            if incremental:
                load_instance_with_external(instance)
            else:
                load_instance_without_external(instance)
                self.ctl.add("instance", [], "edge(X,Y) :- edge(Y,X).")
                self.ctl.ground([("instance", [])])

            if self.debug:
                print("\n === Instance ===")
                print(self.prg)

        self.ctl.load("asp/vertex-cover.lp")
        self.ctl.add("debug", [], "#show in/1.")
        self.ctl.ground([("init", [])])

        if self.debug:
            print("\n === Ground program ===")
            print(self.prg)

    def add_vertex(self, v: int):
        old = Function("vertex", [Number(v)]) in self.ctl.symbolic_atoms

        # self.del_vertex(v)
        with SymbolicBackend(self.ctl.backend()) as backend:
            backend.add_external(Function("vertex", [Number(v)]), TruthValue(True))

        if not old: self.ctl.ground([("add_vertex", [Number(v)])])

    def add_edge(self, v: int, u: int):
        old = Function("edge", [Number(v), Number(u)]) in self.ctl.symbolic_atoms

        # self.del_edge(u,v)
        with SymbolicBackend(self.ctl.backend()) as backend:
            backend.add_external(Function("edge", [Number(v), Number(u)]), TruthValue(True))
            if self.undirected:
                backend.add_external(Function("edge", [Number(u), Number(v)]), TruthValue(True))

        if not old: self.ctl.ground([("add_edge", [Number(v), Number(u)])])

    def del_vertex(self, v: int):
        self.ctl.release_external(Function("vertex", [Number(v)]))

    def del_edge(self, v: int, u: int):
        self.ctl.release_external(Function("edge", [Number(v), Number(u)]))
        if self.undirected:
            self.ctl.release_external(Function("edge", [Number(u), Number(v)]))

    def solve(self, assumptions: List[int] = []) -> bool:
        def on_model(m: Model):
            self.model_count += 1
            if self.show_models: print(m)

        self.model_count = 0
        result = self.ctl.solve(assumptions, on_model=on_model)

        return cast(SolveResult, result).satisfiable == True

    def extract_witness(self) -> List[int]:
        raise NotImplementedError

if __name__ == "__main__":
    def dump_ground_program(vc: SimpleVertexCoverSolver):
        print("\n === Ground program ===")
        print(vc.prg)

    vc = SimpleVertexCoverSolver("asp/instance2.vc", debug = True, show_models=True)

    print(" === Solve the instance ===")
    print(vc.solve(), vc.model_count)

    print(" === Add an edge === ")
    vc.add_vertex(2)
    vc.add_edge(1, 2)
    print(vc.solve(), vc.model_count)

    # dump_ground_program(vc)

    print(" === Delete that edge === ")
    vc.del_edge(1, 2)
    print(vc.solve(), vc.model_count)

    # dump_ground_program(vc)

    print(" === Add that edge again === ")
    vc.add_vertex(2)
    vc.add_edge(1, 2)
    print(vc.solve(), vc.model_count)

    # dump_ground_program(vc)

    print(" === Delete that edge === ")
    vc.del_edge(1, 2)
    print(vc.solve(), vc.model_count)

    dump_ground_program(vc)

    print(" === Add that edge again === ")
    vc.add_vertex(2)
    vc.add_edge(1, 2)
    print(vc.solve(), vc.model_count)

    print("\n === Ground program ===")
    print(vc.prg)