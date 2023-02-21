IPAFAIR: Reentrant Incremental Argumentation Framework API
==========================================================

This repository contains a Python implementation of IPAFAIR, an incremental API
for argumentation framework (AF) solvers. This particular implementation
is based [`clingo`]() on [ASPARTIX](https://www.dbai.tuwien.ac.at/proj/argumentation/systempage/dung.html), 
an '*ASP-based argumentation system for Dung-style abstract argumentation and extensions thereof*', 
by the Databases and Artificial Intelligence Group at TU Wien.

> In particular, IPAFAIR allows for constructing an AF and solving standard reasoning tasks, 
> such as credulous and skeptical acceptance under most widely studied AF semantics, and applying
> dynamic changes (additions and deletions of arguments and attacks) to the AF
> between acceptance queries.

Currently, this implementation admits `naive`, `adm` (admissible) and `stable` semantics.

See `ipafair/` for the original contents of the IPAFAIR repository,
also found [here](https://bitbucket.org/coreo-group/ipafair/src/master/). 
This version merged the top-level contents and the `example/` directory of the original repository.

See `dung/` for the static AF encodings from ASPARTIX and
and `incr-dung/` for the available incrementalized encodings.

See `asp/` for encodings of sample instances.

See `example_*.ipynb` for a usage examples.

## Vertex-Cover
This repository also contains a simple ASP-based incremental 
vertex cover solver, again allowing additions and deletions of 
vertices and edges. 

This toy example serves to demonstrate the general procedure on
how to construct an encoding that admits incremental operations
on the instance and how to feed the data into `clingo`.

The necessary encodings are in `asp/` and `example-vc*.ipynb` 
showcase the solver.