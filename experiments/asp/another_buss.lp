#program init(k).
kernel(X) :- #count{ vertex(Y) : edge(X,Y) } > k, vertex(X).
% :- #count{ 1 : kernel(X) } > k.

next_to_kernel(X) :- vertex(X),
                     1 #count{ vertex(Y) : edge(X,Y), kernel(Y)}.

test(X) :- vertex(X), edge(X,Y),
          not next_to_kernel(X), not kernel(X),
          not next_to_kernel(Y), not kernel(Y).

in(X) :- not out(X), vertex(X).
out(X) :- not in(X), vertex(X).

in(X) :- kernel(X).

out(X) :- vertex(X), next_to_kernel(X).
out(X) :- vertex(X), not test(X).

:- edge(X,Y), not in(X), not in(Y).

#program add_vertex_pre_ground(v).
#external vertex(v).

#program add_vertex(v,k).
#external vertex(v).

kernel(v) :- #count{ vertex(Y) : edge(v,Y) } > k, vertex(v).
next_to_kernel(v) :- vertex(v),
                     1 #count{ vertex(Y) : edge(v,Y), kernel(Y)}.

test(v) :- vertex(v), edge(v,Y),
          not next_to_kernel(v), not kernel(v),
          not next_to_kernel(Y), not kernel(Y).

in(v) :- not out(v), vertex(v).
out(v) :- not in(v), vertex(v).

in(v) :- kernel(v).

out(v) :- vertex(v), next_to_kernel(v).
out(v) :- vertex(v), low(v).

#program add_edge_pre_ground(v,u).
#external edge(v,u).

#program add_edge(v,u).
#external edge(v,u).
:- edge(v,u), not in(v), not in(u).
high(v) :- vertex(u), edge(v,u), not kernel(v).