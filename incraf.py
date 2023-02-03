import ipafair

from clingo.core import TruthValue
from clingo.control import Control
from clingo.symbol import Number, Function, Symbol
from clingo.solving import Model, SolveResult

from clingox.program import Program, ProgramObserver
from clingox.backend import SymbolicBackend

from typing import List, cast, overload

from debug import solve_and_dump_model

class incr_af_solver(ipafair.AFSolver):
    def __init__(self, sigma: str, af_file: str | None = None):
        """
        Initializes an `AFSolver` instance using the initial AF provided in `af_file`
        and the semantics sigma (`CO`, `PR`, or `ST`).
        If `af_file` is `None`, the initial AF is assumed to be empty.
        If `af_file` is not a valid file, changes the state of `AFSolver` to `ERROR`.
        """
        def load_dimacs(af_file: str):
            with open(af_file, "r", encoding="utf-8") as f:
                line_no = 0

                parameters = f.readline().strip().split(" ")
                line_no += 1
                while parameters[0] == "c":
                    parameters = f.readline().strip().split(" ")
                    line_no += 1
                if parameters[0] != "p" or parameters[1] != "af":
                    raise StopIteration

                n = int(parameters[2])
                with SymbolicBackend(self.ctl.backend()) as backend:
                    for v in range(1, n+1):
                        backend.add_external(Function("arg", [Number(v)]), TruthValue(True))

                    for line in f:
                        line_no += 1
                        arguments = line.strip().split(" ")
                        if arguments[0] == "c":
                            continue
                        if len(arguments) != 2:
                            raise SyntaxError("Malformed adjacency list in line " + str(line_no))

                        v, u = arguments
                        v, u = int(v), int(u)

                        self.add_attack(v, u)

        def load_asp(af_file: str):
            with open(af_file, "r", encoding="utf-8") as f:
                tmp = Control()
                tmp.load(af_file)
                tmp.ground()
                tmp.ground([("instance", [])])

                for v in tmp.symbolic_atoms.by_signature("arg", 1):
                    self.add_argument(v.symbol)

                for e in tmp.symbolic_atoms.by_signature("att", 2):
                    self.add_attack(attack=e.symbol)
      
        # self.ctl = Control(arguments=["--models=0", "-ebrave"])
        self.ctl = Control(arguments=["--models=0"])
        self.prg = Program()
        self.ctl.register_observer(ProgramObserver(self.prg))

        if sigma == "naive":
            # self.ctl.load("dung/naive.dl")
            self.ctl.load("incr-dung/naive.lp")
        elif sigma == "adm":
            self.ctl.load("incr-dung/adm.lp")

        if af_file:
            try:
                load_dimacs(af_file)
            except StopIteration:
                load_asp(af_file)

        # self.ctl.add("output_filter", [], "#show in/1.")
    
        self.ctl.ground()

    def __del__(self):
        pass

    def add_argument(self, arg: int | Symbol):
        '''
        Adds the argument `arg` to the current AF instance.
        '''
        if isinstance(arg,int):
            old = Function("arg", [Number(arg)]) in self.ctl.symbolic_atoms

            with SymbolicBackend(self.ctl.backend()) as backend:
                backend.add_external(Function("arg", [Number(arg)]), TruthValue(True))

            if not old: self.ctl.ground([("add_argument", [Number(arg)])])

        elif isinstance(arg,Symbol):
            old = arg in self.ctl.symbolic_atoms
            print(old, arg)

            with SymbolicBackend(self.ctl.backend()) as backend:
                backend.add_external(arg, TruthValue(True))

            if not old: self.ctl.ground([("add_argument", arg.arguments)])

        else:
            raise TypeError("arg must be an argument id (int) or a clingo Symbol.")

    def del_argument(self, arg: int | Symbol):
        '''
        Deletes the argument arg from the current AF instance.
        '''
        if isinstance(arg,int):
            self.ctl.assign_external(Function("arg", [Number(arg)]), False)

            for edge in self.ctl.symbolic_atoms.by_signature("att", 2):
                A, B = edge.symbol.arguments
                if Number(arg) == A or Number(arg) == B:
                    self.ctl.assign_external(Function("att", [A, B]), False)

        elif isinstance(arg,Symbol):
            self.ctl.assign_external(arg, False)

            for edge in self.ctl.symbolic_atoms.by_signature("att", 2):
                A, B = edge.symbol.arguments
                if arg.arguments[0] == A or arg.arguments[0] == B:
                    self.ctl.assign_external(Function("att", [A, B]), False)

        else:
            raise TypeError("arg must be an argument id (int) or a clingo Symbol.")

    def add_attack(self, source: int | None = None, target: int | None = None, attack: Symbol | None = None):
        if isinstance(source, int) and isinstance(target, int) and attack == None:
            old = Function("att", [Number(source), Number(target)]) in self.ctl.symbolic_atoms

            with SymbolicBackend(self.ctl.backend()) as backend:
                backend.add_external(Function("att", [Number(source), Number(target)]), TruthValue(True))

            if not old: self.ctl.ground([("add_attack", [Number(source), Number(target)])])

        elif isinstance(attack, Symbol) and source == None and target == None:
            old = attack in self.ctl.symbolic_atoms
            print(old, attack)

            with SymbolicBackend(self.ctl.backend()) as backend:
                backend.add_external(attack, TruthValue(True))

            if not old: self.ctl.ground([("add_attack", attack.arguments)])

        elif isinstance(attack, Symbol) and (source != None or target != None):
            raise TypeError("attack and (source,target) parameters are mutually exclusive.")

        else:
            raise Exception

    def del_attack(self, source: int | None = None, target: int | None = None, attack: Symbol | None = None):
        if isinstance(source, int) and isinstance(target, int) and attack == None:
            self.ctl.assign_external(Function("att", [Number(source), Number(target)]), False)

        elif isinstance(attack, Symbol) and source == None and target == None:
            self.ctl.assign_external(attack, False)

        elif isinstance(attack, Symbol) and (source != None or target != None):
            raise TypeError("attack and (source,target) parameters are mutually exclusive.")

        else:
            raise Exception

    def __solve(self, assumps: List[int] = []) -> bool:
        def on_model(m: Model):
            self.model_count += 1
            print("Model:", m)

        self.model_count = 0
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

    af = incr_af_solver("adm", "asp/af2.lp")
    dump_ground_program(af)

    print("\n\n === Solve credulously ===")
    print(af.solve_cred(), af.model_count)
    print("\n\n === Solve skeptically === ")
    print(af.solve_skept(), af.model_count)
    # solve_and_dump_model(af.ctl)