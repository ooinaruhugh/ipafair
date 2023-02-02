%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% ASP encoding for (minimal) dominating sets
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#program problem.
%% Make edges implicitly undirected.
edge(X,Y) :- edge(Y,X).

%% Guess a solution set S.
in(X) :- not out(X), vertex(X).
out(X) :- not in(X), vertex(X).

%% A vertex not in the solution set has to be adjacent.
% in(Y) :- not in(X), edge(X,Y).

%% A non-dominating vertex has to have at least one dominating neighbor
:- not in(Y), vertex(Y), #count{ in(X) : edge(X,Y) } < 1.

%% Introduce some minimality conditions. 
%% Basically, cross out every edge that is covered.
%not in(Y) :- edge(X,Y), in(X).