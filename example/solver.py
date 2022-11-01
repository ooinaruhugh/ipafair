import ipafair
import os
from ctypes import cdll, c_void_p, c_int

LIBNAME = "libipafairsolver.so"
LIBPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), LIBNAME)

semantics_to_code = {"AD": 0, "CO": 1, "PR": 2, "ST": 3, "SST": 4, "STG": 5}

class NaiveSolver(ipafair.AFSolver):
    def __init__(self, sigma: str, apx_file: str = None):
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
        self.arg_to_int = {}
        self.status = 0
        self.n_args = 0
        self.last_call = ""

        if apx_file is not None:
            contents = [line for line in open(apx_file).read().split("\n")]
            args = [line.replace("arg(",").").replace(").","") for line in contents if line.startswith("arg")]
            atts = [line.replace("att(",").").replace(").","") for line in contents if line.startswith("att")]
            for arg in args:
                self.add_argument(arg)
            for att in atts:
                self.add_attack(att.split(","))

    def __del__(self):
        self.lib.ipafair_release(self.solver)

    def add_argument(self, arg: str):
        if arg not in self.arg_to_int:
            self.n_args += 1
            self.arg_to_int[arg] = self.n_args
        self.lib.ipafair_add_argument(self.solver, self.arg_to_int[arg])

    def del_argument(self, arg: str):
        self.lib.ipafair_del_argument(self.solver, self.arg_to_int[arg])
        self.arg_to_int.pop(arg, None)

    def add_attack(self, att):
        self.lib.ipafair_add_attack(self.solver, self.arg_to_int[att[0]], self.arg_to_int[att[1]])

    def del_attack(self, att):
        self.lib.ipafair_del_attack(self.solver, self.arg_to_int[att[0]], self.arg_to_int[att[1]])

    def solve_cred(self, assumps) -> bool:
        for arg in assumps:
            self.lib.ipafair_assume(self.solver, self.arg_to_int[arg])
        self.status = self.lib.ipafair_solve_cred(self.solver)
        self.last_call = "cred"
        if self.status == 10:
            return True
        if self.status == 20:
            return False

    def solve_skept(self, assumps) -> bool:
        for arg in assumps:
            self.lib.ipafair_assume(self.solver, self.arg_to_int[arg])
        self.status = self.lib.ipafair_solve_skept(self.solver)
        self.last_call = "skept"
        if self.status == 10:
            return True
        if self.status == 20:
            return False

    def extract_witness(self):
        if (self.status == 10 and self.last_call == "cred") or (self.status == 20 and self.last_call == "skept"):
            extension = []
            for arg in self.arg_to_int:
                if self.lib.ipafair_val(self.solver, self.arg_to_int[arg]) > 0:
                    extension.append(arg)
            return extension
