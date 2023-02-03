import ipafair

from clingo.core import TruthValue
from clingo.control import Control
from clingo.symbol import Number, Function
from clingo.solving import Model, SolveResult

from clingox.program import Program, ProgramObserver
from clingox.backend import SymbolicBackend

from typing import List, cast

from debug import solve_and_dump_model

class incr_af_solver: #(ipafair.AFSolver):
    def __init__(self, sigma: str, af_file: str | None = None):
        """
        Initializes an `AFSolver` instance using the initial AF provided in `af_file`
        and the semantics sigma (`CO`, `PR`, or `ST`).
        If `af_file` is `None`, the initial AF is assumed to be empty.
        If `af_file` is not a valid file, changes the state of `AFSolver` to `ERROR`.
        """
        def load_dimacs(af_file: str):
            with open(af_file, "r", encoding="utf-8") as f:
                parameters = f.readline().strip().split(" ")
                while parameters[0] == "c":
                    parameters = f.readline().strip().split(" ")
                if parameters[0] != "p" or parameters[1] != "af":
                    raise Exception

                n = int(parameters[2])
                with SymbolicBackend(self.ctl.backend()) as backend:
                    for v in range(1, n+1):
                        backend.add_external(Function("arg", [Number(v)]), TruthValue(True))

                    for line in f:
                        arguments = line.strip().split(" ")
                        if arguments[0] == "c":
                            continue
                        if len(arguments) != 2:
                            raise Exception

                        v, u = arguments
                        v, u = int(v), int(u)

                        self.add_attack(v, u)

        def load_asp(ctl: Control, af_file: str):
            with open(af_file, "r", encoding="utf-8") as f:
                tmp = Control()
                tmp.load(af_file)
                tmp.ground()
                tmp.ground([("instance", [])])

                with SymbolicBackend(ctl.backend()) as backend:
                    for v in tmp.symbolic_atoms.by_signature("arg", 1):
                        backend.add_external(v.symbol, TruthValue(True))

                    for e in tmp.symbolic_atoms.by_signature("att", 2):
                        backend.add_external(e.symbol, TruthValue(True))
        
        self.ctl = Control(arguments=["--models=0"])
        self.prg = Program()
        self.ctl.register_observer(ProgramObserver(self.prg))

        if af_file:
            try:
                load_dimacs(af_file)
            except:
                # self.ctl = Control(arguments=["--models=0", "-ebrave"])
                self.ctl = Control(arguments=["--models=0"])
                self.prg = Program()
                self.ctl.register_observer(ProgramObserver(self.prg))
                load_asp(self.ctl, af_file)

        self.ctl.add("output_filter", [], "#show in/1.")
        
        if sigma == "naive":
            self.ctl.load("dung/naive.dl")
            self.ctl.load("incr-dung/naive.lp")

        self.ctl.ground()

    def __del__(self):
        pass

    def add_argument(self, arg: int):
        '''
        Adds the argument `arg` to the current AF instance.
        '''
        old = Function("arg", [Number(arg)]) in self.ctl.symbolic_atoms

        # self.del_vertex(v)
        with SymbolicBackend(self.ctl.backend()) as backend:
            backend.add_external(Function("arg", [Number(arg)]), TruthValue(True))

        if not old: self.ctl.ground([("add_arg", [Number(arg)])])

    def del_argument(self, arg: int):
        '''
        Deletes the argument arg from the current AF instance.
        '''
        self.ctl.assign_external(Function("arg", [Number(arg)]), False)

        for edge in self.ctl.symbolic_atoms.by_signature("att", 2):
            A, B = edge.symbol.arguments
            if Number(arg) == A or Number(arg) == B:
                self.ctl.assign_external(Function("att", [A, B]), False)

    def add_attack(self, source: int, target: int):
        old = Function("att", [Number(source), Number(target)]) in self.ctl.symbolic_atoms

        with SymbolicBackend(self.ctl.backend()) as backend:
            backend.add_external(Function("att", [Number(source), Number(target)]), TruthValue(True))

        if not old: self.ctl.ground([("add_attack", [Number(source), Number(target)])])

    def del_attack(self, source: int, target: int):
        self.ctl.assign_external(Function("att", [Number(source), Number(target)]), False)

    def __solve(self, assumps: List[int] = []) -> bool:
        def on_model(m: Model):
            print(m)

        result = self.ctl.solve(assumps, on_model=on_model)
        return cast(SolveResult, result).satisfiable == True

    def solve_cred(self, assumps: List[int] = []) -> bool:
        '''
        Solves the current AF instance under the specified semantics in the
        credulous reasoning mode under assumptions that all arguments in assumps
        are contained in an extension.
        Returns `True` if the answer is "yes" and `False` if the answer is "no".
        Other return codes indicate that the solver is in state `ERROR`.
        '''
        self.ctl.configuration.solve.enum_mode = "brave"
        return self.__solve(assumps)

    def solve_skept(self, assumps: List[int] = []) -> bool:
        '''
        Solves the current AF instance under the specified semantics in the
        skeptical reasoning mode under assumptions that all arguments in assumps
        are contained in all extensions.
        Returns `True` if the answer is "yes" and `False` if the answer is "no".
        Other return codes indicate that the solver is in state `ERROR`.
        '''
        self.ctl.configuration.solve.enum_mode = "cautious"
        return self.__solve(assumps)

    def extract_witness(self) -> List[int]:
        '''
        If the previous call of `solve_cred` returned `True`, or the previous call to
        `solve_skept` returned `False`, returns the witnessing extension.
        '''
        raise NotImplementedError



if __name__ == "__main__":
    def dump_ground_program(solver):
        print("\n === Ground program ===")
        print(solver.prg)

    af = incr_af_solver("naive", "asp/af1.lp")
    dump_ground_program(af)

    print("\n\n === Solve naively credulously ===")
    af.solve_cred()
    print("\n\n === Solve naively skeptically === ")
    af.solve_skept()
    # solve_and_dump_model(af.ctl)