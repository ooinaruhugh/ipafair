%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Encoding for admissible extensions
% broken apart to selectively add the parts 
% for arguments and attacks
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#program add_argument(v).
%% Guess a set S \subseteq A
in(v) :- not out(v), arg(v).
out(v) :- not in(v), arg(v).


#program add_attack(v,u).
%% S has to be conflict-free
:- in(v), in(u), att(v,u).

%% The argument x is defeated by the set S
defeated(v) :- in(u), att(Y,v).

%% The argument x is not defended by S
not_defended(v) :- att(Y,v), not defeated(u).

%% All arguments x \in S need to be defended by S
:- in(v), not_defended(v).