# This file is part of IPAFAIR, an incremental API for AF solvers.
# See LICENSE.md for rights to use this software.

from abc import ABC, abstractmethod
from typing import Tuple, List

class AFSolver(ABC):

    # Initializes an AFSolver instance using the initial AF provided apx_file
    # and the semantics sigma ("CO", "PR", or "ST").
    # If apx_file is None, the initial AF is assumed to be empty.
    # If apx_file is not a valid file, changes the state of AFSolver to ERROR.
    @abstractmethod
    def __init__(self, sigma: str, apx_file: str = None):
        raise NotImplementedError

    # Deletes an AFSolver instance.
    @abstractmethod
    def __del__(self):
        pass

    # Adds the argument arg to the current AF instance.
    @abstractmethod
    def add_argument(self, arg: str):
        raise NotImplementedError

    # Deletes the argument arg from the current AF instance.
    @abstractmethod
    def del_argument(self, arg: str):
        raise NotImplementedError

    # Adds the attack att to the current AF instance.
    @abstractmethod
    def add_attack(self, att: Tuple[str, str]):
        raise NotImplementedError

    # Deletes the attack att from the current AF instance.
    @abstractmethod
    def del_attack(self, att: Tuple[str, str]):
        raise NotImplementedError

    # Solves the current AF instance under the specified semantics in the
    # credulous reasoning mode under assumptions that all arguments in assumps
    # are contained in an extension.
    # Returns True if the answer is "yes" and False if the answer is "no".
    # Other return codes indicate that the solver is in state ERROR.
    @abstractmethod
    def solve_cred(self, assumps: List[str]) -> bool:
        raise NotImplementedError

    # Solves the current AF instance under the specified semantics in the
    # skeptical reasoning mode under assumptions that all arguments in assumps
    # are contained in all extensions.
    # Returns True if the answer is "yes" and False if the answer is "no".
    # Other return codes indicate that the solver is in state ERROR.
    @abstractmethod
    def solve_skept(self, assumps: List[str]) -> bool:
        raise NotImplementedError

    # If the previous call of solve_cred returned True, or the previous call to
    # solve_skept returned False, returns the witnessing extension.
    @abstractmethod
    def extract_witness(self) -> List[str]:
        raise NotImplementedError