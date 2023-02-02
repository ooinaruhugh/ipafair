%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% ASP encoding for (minimal) vertex cover
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#program init.

%% Guess a vertex cover S.
% #external in(X) : not out(X), vertex(X).
in(X) :- not out(X), vertex(X).
% #external out(X) : not in(X), vertex(X).
out(X) :- not in(X), vertex(X).

%% Test wheter every edge has an incident vertex in S.
:- edge(X,Y), not in(X), not in(Y).

%% Introduce some minimality conditions. 
%% Basically, cross out every edge that is covered.
% not in(Y) :- edge(X,Y), in(X).

#program add_vertex(v).
in(v) :- not out(v), vertex(v).
out(v) :- not in(v), vertex(v).

#program add_edge(u,v).
:- edge(u,v), not in(u), not in(v).