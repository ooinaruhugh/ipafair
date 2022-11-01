This directory contains a naive AF solver in C++ (`solver.cpp`) which implements
the C version of IPAFAIR, and a Python wrapper (`solver.py`) which allows for
calling the C++ solver via the Python version of IPAFAIR.

Note that this implementation naively writes the current AF to a temporary file
and calls an external AF solver on it to respond to acceptance queries.
In other words, this implementation is fully non-incremental. Its purpose is to
show how to build a C-based AF solver, and write a corresponding Python wrapper.

To compile the dynamic library, please issue

`AF_SOLVER=/path/to/af_solver make`

where `/path/to/af_solver` is a binary to an AF solver which fulfills the ICCMA
input and output format requirements and accepts `.apx` files as input AFs.

See also `test.py` for usage examples.