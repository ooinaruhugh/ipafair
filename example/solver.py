import ipafair
import os
from ctypes import cdll, c_void_p, c_int

LIBNAME = "libipafairsolver.so"
LIBPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), LIBNAME)

semantics_to_code = {"AD": 0, "CO": 1, "PR": 2, "ST": 3, "SST": 4, "STG": 5}

class NaiveSolver(ipafair.AFSolver):
    def __init__(self, sigma: str, af_file: str = None):
        if not os.path.exists(LIBPATH):
            raise IOError("Shared library not found. Please run 'make' to build.")

        self.lib = cdll.LoadLibrary(LIBPATH)
        self.lib.ipafair_init.restype = c_void_p
        self.lib.ipafair_init.argtypes = []
        self.lib.ipafair_release.argtypes = [c_void_p]
        self.lib.ipafair_set_semantics.argtypes = [c_void_p, c_int]
        self.lib.ipafair_add_argument.argtypes = [c_void_p, c_int]
        self.lib.ipafair_del_argument.argtypes = [c_void_p, c_int]
        self.lib.ipafair_add_attack.argtypes = [c_void_p, c_int, c_int]
        self.lib.ipafair_del_attack.argtypes = [c_void_p, c_int, c_int]
        self.lib.ipafair_assume.argtypes = [c_void_p, c_int]
        self.lib.ipafair_solve_cred.restype = c_int
        self.lib.ipafair_solve_cred.argtypes = [c_void_p]
        self.lib.ipafair_solve_skept.restype = c_int
        self.lib.ipafair_solve_skept.argtypes = [c_void_p]
        self.lib.ipafair_val.restype = c_int
        self.lib.ipafair_val.argtypes = [c_void_p, c_int]

        self.solver = self.lib.ipafair_init()
        self.lib.ipafair_set_semantics(self.solver, semantics_to_code[sigma])
        self.status = 0
        self.last_call = ""

        if af_file is not None:
            contents = [line.strip() for line in open(af_file).read().split("\n") if not line.startswith("#")]
            p_line = contents[0]
            assert(p_line.startswith("p af "))
            self.n = int(p_line[5:])
            args = list(range(1, self.n+1))
            atts = [ list(map(int, line.split())) for line in contents[1:] ]
            assert(all(len(att) == 2 for att in atts))
            for a in args:
                self.add_argument(a)
            for s,t in atts:
                self.add_attack(s,t)

    def __del__(self):
        self.lib.ipafair_release(self.solver)

    def add_argument(self, arg: int):
        self.lib.ipafair_add_argument(self.solver, arg)

    def del_argument(self, arg: int):
        self.lib.ipafair_del_argument(self.solver, arg)

    def add_attack(self, source: int, target: int):
        self.lib.ipafair_add_attack(self.solver, source, target)

    def del_attack(self, source: int, target: int):
        self.lib.ipafair_del_attack(self.solver, source, target)

    def solve_cred(self, assumps) -> bool:
        for a in assumps:
            self.lib.ipafair_assume(self.solver, a)
        self.status = self.lib.ipafair_solve_cred(self.solver)
        self.last_call = "cred"
        if self.status == 10:
            return True
        if self.status == 20:
            return False

    def solve_skept(self, assumps) -> bool:
        for a in assumps:
            self.lib.ipafair_assume(self.solver, a)
        self.status = self.lib.ipafair_solve_skept(self.solver)
        self.last_call = "skept"
        if self.status == 10:
            return True
        if self.status == 20:
            return False

    def extract_witness(self):
        if (self.status == 10 and self.last_call == "cred") or (self.status == 20 and self.last_call == "skept"):
            extension = []
            for a in range(1, self.n+1):
                if self.lib.ipafair_val(self.solver, a) > 0:
                    extension.append(arg)
            return extension
