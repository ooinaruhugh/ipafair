#program instance.
vertex(1..9).
edge(1,(2;4;6;8)).
edge(2,3).
edge(3,(4;6;8)).
% edge(4,(1;3)). 
% edge(5,).
edge(6,7).
edge(7,8).
% edge(8,(1;3)).
% edge(9,).

edge(X,Y) :- edge(Y,X).