from ipafair import AFSolver

from clingo.core import TruthValue
from clingo.control import Control
from clingo.symbol import Number, Function, Symbol
from clingo.solving import Model, SolveHandle

from clingox.program import Program, ProgramObserver
from clingox.backend import SymbolicBackend

from typing import List, cast

def make_argument(name: int | str) -> Symbol:
    """
    Creates a clingo `Symbol` representing an argument `name`.
    """
    if isinstance(name, int):
        return Function("arg", [Number(name)])
    elif isinstance(name, str):
        return Function("arg", [Function(name, [])])
    else:
        raise TypeError("Arguments can only be named by strings or integers.")

def make_attack(source: int | str, target: int | str) -> Symbol:
    """
    Creates a clingo `Symbol` representing an attack from argument `source` to argument `target`.
    """
    if isinstance(source, int):
        s = Number(source)
    elif isinstance(source, str):
        s = Function(source, [])
    else:
        raise TypeError("Arguments can only be named by strings or integers.")

    if isinstance(target, int):
        t = Number(target)
    elif isinstance(target, str):
        t = Function(target, [])
    else:
        raise TypeError("Arguments can only be named by strings or integers.")

    return Function("att", [s, t])

class IncrAFSolver(AFSolver):
    def __init__(self, sigma: str, af_file: str | None = None):
        """
        Initializes an `AFSolver` instance using the initial argumentation framework (AF) provided in `af_file`
        and the semantics sigma (`CO`, `PR`, or `ST`).
        If `af_file` is `None`, the initial AF is assumed to be empty.
        If `af_file` is not a valid file, changes the state of `AFSolver` to `ERROR`.
        """
        def load_dimacs(af_file: str):
            """
            An internal method to load an AF from a DIMACS-like format.
            """
            with open(af_file, "r", encoding="utf-8") as f:
                line_no = 0

                # Initialization step, getting the first `p` line from the input.
                parameters = f.readline().strip().split(" ")
                line_no += 1
                while parameters[0] == "c":
                    parameters = f.readline().strip().split(" ")
                    line_no += 1
                if parameters[0] != "p" or parameters[1] != "af":
                    raise StopIteration

                n = int(parameters[2])
                with SymbolicBackend(self.ctl.backend()) as backend:
                    # We initialize the arguments according to the header
                    for v in range(1, n+1):
                        backend.add_external(Function("arg", [Number(v)]), TruthValue(True))

                    # Every line in the input constitutes one attack.
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
            """
            An internal method to load an AF from a given logic program.
            """
            # We basically let the grounder do the parsing of an instance file by throwing 
            # the instance into a temporary context to get objects for the atoms.
            # Then, we feed those into the actual solver context, as externals.
            with open(af_file, "r", encoding="utf-8") as f:
                tmp = Control()
                tmp.load(af_file)

                # We expect either the instance to be in a flat file,
                # or the instance to be contained in a program block named "instance".
                tmp.ground()
                tmp.ground([("instance", [])])

                for v in tmp.symbolic_atoms.by_signature("arg", 1):
                    self.add_argument(v.symbol)

                for e in tmp.symbolic_atoms.by_signature("att", 2):
                    self.add_attack(attack=e.symbol)
      
        self.ctl = Control(arguments=["--models=0"])

        # `Program` is for pretty-printing a ground program. Useful for debugging.
        self.prg = Program()
        self.ctl.register_observer(ProgramObserver(self.prg))

        if sigma == "naive":
            self.ctl.load("incr-dung/naive.lp")
        elif sigma == "adm":
            self.ctl.load("incr-dung/adm.lp")
        elif sigma == "stable":
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

        # When solving credulously or skeptically, we only return `True` or `False`.
        # A witness can be found with `extract_witness` and this is where it is stored.
        self.witness: List[Symbol] = []

    def __del__(self):
        pass

    def add_argument(self, arg: int | str | Symbol):
        '''
        Adds the argument `arg` to the current AF instance.

        If `arg` is given as `int` or `str`, it gets wrapped as a clingo `Symbol` first.

        If directly providing a clingo `Symbol`, no sanity checks are performed.
        '''
        if isinstance(arg,int) or isinstance(arg,str):
            arg = make_argument(arg)
        elif not isinstance(arg,Symbol):
            raise TypeError("arg must be an argument id (int or str) or a clingo Symbol.")

        old = arg in self.ctl.symbolic_atoms

        with SymbolicBackend(self.ctl.backend()) as backend:
            backend.add_external(arg, TruthValue(True))
        
        if not old: self.ctl.ground([("add_argument", arg.arguments)])

    def del_argument(self, arg: int | str | Symbol):
        '''
        Deletes the argument `arg` from the current AF instance.

        If `arg` is given as `int` or `str`, it gets wrapped as a clingo `Symbol` first.

        If directly providing a clingo `Symbol`, no sanity checks are performed.
        '''
        if isinstance(arg,int) or isinstance(arg,str):
            arg = make_argument(arg)
        elif not isinstance(arg,Symbol):
            raise TypeError("arg must be an argument id (int or str) or a clingo Symbol.")

        self.ctl.assign_external(arg, False)

        for edge in self.ctl.symbolic_atoms.by_signature("att", 2):
            A, B = edge.symbol.arguments
            if arg.arguments[0] == A or arg.arguments[0] == B:
                self.ctl.assign_external(Function("att", [A, B]), False)

    def add_attack(self, source: int | str | None = None, target: int | str | None = None, attack: Symbol | None = None):
        '''
        Adds an attack from arguments `source` to `target` to the current AF instance.

        `source` and `target` can be given as `int` or `str`. A pair of `source` and `target` 
        and `attack` are mutually exclusive.

        If directly providing a clingo `Symbol`, no sanity checks are performed.
        '''
        if source != None and target != None and attack == None:
            attack = make_attack(source, target)
        elif isinstance(attack, Symbol) and (source != None or target != None):
            raise TypeError("attack and (source,target) parameters are mutually exclusive.")
        
        assert(isinstance(attack, Symbol))
        old = attack in self.ctl.symbolic_atoms

        with SymbolicBackend(self.ctl.backend()) as backend:
            backend.add_external(attack, TruthValue(True))

        if not old: self.ctl.ground([("add_attack", attack.arguments)])        

    def del_attack(self, source: int | str | None = None, target: int | str | None = None, attack: Symbol | None = None):
        '''
        Deletes an attack from arguments `source` to `target` to the current AF instance.

        `source` and `target` can be given as `int` or `str`. A pair of `source` and `target` 
        and `attack` are mutually exclusive.

        If directly providing a clingo `Symbol`, no sanity checks are performed.
        '''
        if source != None and target != None and attack == None:
            attack = make_attack(source, target)
        elif isinstance(attack, Symbol) and (source != None or target != None):
            raise TypeError("attack and (source,target) parameters are mutually exclusive.")
        
        assert(isinstance(attack, Symbol))

        self.ctl.assign_external(attack, False)

    def solve_enum(self, assumps: List[int] = [], verbose = False) -> List[List[Symbol]]:
        '''
        Solves the current AF instance and enumerates all models 
        under assumptions that all arguments in `assumps` are contained in an extension.
        
        Returns `True` if the answer is "yes" and `False` if the answer is "no".
        Other return codes indicate that the solver is in state `ERROR`.
        
        The `verbose` flag causes the model(s) to be pretty printed during the `solve` call.
        '''
        self.ctl.configuration.solve.enum_mode = "record"

        def on_model(m: Model):
            if verbose: print(f"DEBUG Model {m.number}:", m)

        result = cast(SolveHandle, self.ctl.solve(assumps, on_model=on_model, yield_=True))

        models = []

        for i, m in enumerate(result):
            models.append(list(m.symbols(shown=True)))

        return models

    def __prepare_pretty_print_model(self, model: List[Symbol]):
        return [f"{s.name}({','.join(map(str, s.arguments))})" for s in model]

    def solve_cred(self, assumps: List[int] = [], verbose = False) -> bool:
        '''
        Solves the current AF instance under the specified semantics in the
        credulous reasoning mode under assumptions that all arguments in `assumps`
        are contained in an extension.

        Returns `True` if the answer is "yes" and `False` if the answer is "no".

        Other return codes indicate that the solver is in state `ERROR`.

        The `verbose` flag causes the model(s) to be pretty printed during the `solve` call.
        '''
        self.ctl.configuration.solve.enum_mode = "brave"

        model: List[Symbol] = []
        def on_model(m: Model):
            nonlocal model
            model = list(m.symbols(shown=True))
        
        self.ctl.solve(assumps, on_model = on_model)

        if verbose and len(model) > 0: print("DEBUG Credulous arguments:", *self.__prepare_pretty_print_model(model))
        self.witness = model

        return len(model) != 0

    def solve_skept(self, assumps: List[int] = [], verbose = False) -> bool:
        '''
        Solves the current AF instance under the specified semantics in the
        skeptical reasoning mode under assumptions that all arguments in `assumps`
        are contained in all extensions.

        Returns `True` if the answer is "yes" and `False` if the answer is "no".

        Other return codes indicate that the solver is in state `ERROR`.

        The `verbose` flag causes the model(s) to be pretty printed during the `solve` call.
        '''
        self.ctl.configuration.solve.enum_mode = "cautious"

        model: List[Symbol] = []
        def on_model(m: Model):
            nonlocal model
            model = list(m.symbols(shown=True))
        
        self.ctl.solve(assumps, on_model = on_model)

        if verbose and len(model) > 0: print("DEBUG Skeptical arguments:", *self.__prepare_pretty_print_model(model))
        self.witness = model

        return len(model) != 0

    def extract_witness(self) -> List[int]:
        '''
        If the previous call of `solve_cred` returned `True`, or the previous call to
        `solve_skept` returned `False`, returns the witnessing extension.
        '''
        return self.witness

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

    print("=== Solve and enumerate the static thing ===")
    # clingo outputs models by specifying a hook for callbacks whenever a model is accessed.
    # Here, we just access the running number of the model and print that.
    def on_model(m: Model):
        print(f"Model {m.number}:", m)
    ctl.solve(on_model=on_model)

    # Now, we do the same incrementally
    af = IncrAFSolver(semantic, filename)

    # print("\n === Ground incremental program ===")
    # print(af.prg)

    print("\n\n === Solve and enumerate ===")
    af.solve_enum(verbose=True)

    print("\n\n === Solve credulously ===")
    print(af.solve_cred(verbose=True))

    print("\n\n === Solve skeptically ===")
    print(af.solve_skept(verbose=True))