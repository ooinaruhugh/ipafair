import ipafair

from clingo.core import TruthValue
from clingo.control import Control
from clingo.symbol import Number, Function, Symbol, String
from clingo.solving import Model, SolveResult, SolveHandle

from clingox.program import Program, ProgramObserver
from clingox.backend import SymbolicBackend

from itertools import product

from typing import List, cast, overload

from debug import solve_and_dump_model, dump_symbolic_atoms

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
                            raise SyntaxError("Malformed attack in line " + str(line_no))

                        v, u = arguments
                        v, u = int(v), int(u)

                        self.add_attack(v, u)

        def load_asp(af_file: str):
            # We basically throw the instance into a temporary
            # context to get objects for the atoms.
            # Then, we feed those into the actual solver context,
            # as externals.
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
            # self.ctl.load("dung/adm.dl")
            self.ctl.load("incr-dung/adm.lp")
        elif sigma == "stable":
            # self.ctl.load("dung/adm.dl")
            self.ctl.load("incr-dung/stable.lp")
        else:
            raise KeyError("Semantics name is not known")

        if af_file:
            try:
                load_dimacs(af_file)
            except StopIteration:
                load_asp(af_file)

        self.ctl.add("output_filter", [], "#show in/1.")
    
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
            # self.ctl.ground()

        elif isinstance(arg,Symbol):
            old = arg in self.ctl.symbolic_atoms

            with SymbolicBackend(self.ctl.backend()) as backend:
                backend.add_external(arg, TruthValue(True))

            if not old: self.ctl.ground([("add_argument", arg.arguments)])
            # self.ctl.ground()

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
            # self.ctl.ground()

        elif isinstance(attack, Symbol) and source == None and target == None:
            old = attack in self.ctl.symbolic_atoms

            with SymbolicBackend(self.ctl.backend()) as backend:
                backend.add_external(attack, TruthValue(True))

            if not old: self.ctl.ground([("add_attack", attack.arguments)])
            # self.ctl.ground()

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

    # def __solve(self, assumps: List[int] = []) -> SolveHandle | SolveResult:
    #     def on_model(m: Model):
    #         self.model_count += 1
    #         print("Model:", m)

    #     self.model_count = 0
    #     return self.ctl.solve(assumps, on_model=on_model) 

    def solve_enum(self, assumps: List[int] = []) -> List[List[Symbol]]:
        '''
        Solves the current AF instance and enumerates all models 
        under assumptions that all arguments in `assumps` are contained in an extension.
        Returns `True` if the answer is "yes" and `False` if the answer is "no".
        Other return codes indicate that the solver is in state `ERROR`.
        '''
        self.ctl.configuration.solve.enum_mode = "record"

        def on_model(m: Model):
            print(f"DEBUG Model {m.number}:", m)
            # pass

        result = cast(SolveHandle, self.ctl.solve(assumps, on_model=on_model, yield_=True))

        models = []

        for i, m in enumerate(result):
            # print(f"Model {i}:", m)
            models.append(list(m.symbols(shown=True)))

        return models

    def __prepare_pretty_print_model(self, model: List[Symbol]):
        return [f"{s.name}({','.join(map(str, s.arguments))})" for s in model]

    def solve_cred(self, assumps: List[int] = []) -> bool:
        '''
        Solves the current AF instance under the specified semantics in the
        credulous reasoning mode under assumptions that all arguments in `assumps`
        are contained in an extension.
        Returns `True` if the answer is "yes" and `False` if the answer is "no".
        Other return codes indicate that the solver is in state `ERROR`.
        '''
        self.ctl.configuration.solve.enum_mode = "brave"
        model: List[Symbol] = []
        def on_model(m: Model):
            nonlocal model
            model = list(m.symbols(shown=True))
        
        self.ctl.solve(assumps, on_model = on_model)

        print("DEBUG Credulous arguments:", *self.__prepare_pretty_print_model(model))

        return len(model) != 0

    def solve_skept(self, assumps: List[int] = []) -> bool:
        '''
        Solves the current AF instance under the specified semantics in the
        skeptical reasoning mode under assumptions that all arguments in `assumps`
        are contained in all extensions.
        Returns `True` if the answer is "yes" and `False` if the answer is "no".
        Other return codes indicate that the solver is in state `ERROR`.
        '''
        self.ctl.configuration.solve.enum_mode = "cautious"

        model: List[Symbol] = []
        def on_model(m: Model):
            nonlocal model
            model = list(m.symbols(shown=True))
        
        self.ctl.solve(assumps, on_model = on_model)

        print("DEBUG Skeptical arguments:", *self.__prepare_pretty_print_model(model))
        
        return len(model) != 0

    def extract_witness(self) -> List[int]:
        '''
        If the previous call of `solve_cred` returned `True`, or the previous call to
        `solve_skept` returned `False`, returns the witnessing extension.
        '''
        raise NotImplementedError

if __name__ == "__main__":
    filename = "asp/af3.lp"
    semantic = "naive"

    # First, load the static version of this af, as comparison
    ctl = Control(arguments=["--models=0"])
    prg = Program()
    ctl.register_observer(ProgramObserver(prg))

    ctl.load(filename)
    ctl.load(f"dung/{semantic}.dl")
    ctl.load("asp/filter.lp")
    ctl.ground()

    # print("\n === Ground static program ===")
    # print(prg)

    print("\n\n === Solve and enumerate the static thing ===")
    def on_model(m: Model):
        print(f"Model {m.number}:", m)
    ctl.solve(on_model=on_model)

    # Now, we do the same incrementally
    af = incr_af_solver(semantic, filename)
    # print("\n === Ground incremental program ===")
    # print(af.prg)

    print("\n\n === Solve and enumerate ===")
    af.solve_enum()

    print("\n\n === Solve credulously ===")
    print(af.solve_cred())

    print("\n\n === Solve skeptically ===")
    print(af.solve_skept())

    # Loading instance as externals but grounding normally
    # ctl1 = Control(arguments=["--models=0"])
    # prg1 = Program()
    # ctl1.register_observer(ProgramObserver(prg1))

    # ctl1.load("asp/af3-alt.lp")
    # ctl1.load(f"dung/{semantic}.dl")
    # ctl1.load("asp/filter.lp")
    # ctl1.ground()

    # print("\n === Ground incremental program, second try ===")
    # print(prg1)

    # print("\n\n === Solve and enumerate the static thing ===")
    # def on_model(m: Model):
    #     print(f"Model {m.number}:", m)
    # ctl1.solve(on_model=on_model)