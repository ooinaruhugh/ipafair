%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Encoding for naive extensions
% broken apart to selectively add the parts 
% for arguments and attacks
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#program add_argument(v).
%% Guess a set S \subseteq A
in(v) :- not out(v), arg(v).
out(v) :- not in(v), arg(v).

#program add_attack(v, u).
%% S has to be conflict-free
:- in(v), in(u), att(v,u).

%% Check Maximality
okOut(v) :- in(u), att(u,v).
okOut(v) :- in(u), att(v,u).
okOut(v) :- att(v,v).
:-  out(v), not okOut(v).