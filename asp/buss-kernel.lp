#program buss(k).
kernel(X) :- #count{ vertex(Y) : edge(X,Y) } > k, vertex(X).
:- #count{ 1 : kernel(X) } > k.

next_to_kernel(X) :- vertex(X),
                     1 #count{ vertex(Y) : edge(X,Y), kernel(Y)}.

low(X) :- vertex(X), 
          not kernel(X), 
          #count{ vertex(Y) : edge(X,Y), not high_deg(Y)} 0.

test(X) :- vertex(X), not kernel(X), not next_to_kernel(X), not low(X).

in(X) :- not out(X), vertex(X).
out(X) :- not in(X), vertex(X).

in(X) :- kernel(X).

out(X) :- vertex(X), next_to_kernel(X).
out(X) :- vertex(X), low(X).

:- edge(X,Y), not in(X), not in(Y).

#program add_vertex_pre_ground(v).
#external vertex(v).

#program add_vertex(v).
#external vertex(v).

#program add_edge_pre_ground(v,u).
#external edge(v,u).

#program add_edge(v,u).
#external edge(v,u).