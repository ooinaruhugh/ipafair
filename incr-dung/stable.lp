%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Encoding for stable extensions
% broken apart to selectively add the parts 
% for arguments and attacks
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#program add_argument(v).
%% Guess a set S \subseteq A
in(v) :- not out(v), arg(v).
out(v) :- not in(v), arg(v).

%% S defeats all arguments which do not belong to S
#external defeated(v).
:- out(v), not defeated(v).

%% END add_argument

#program add_attack(v,u).
%% S has to be conflict-free
:- in(v), in(u), att(v,u).

%% The argument v is defeated by the set S
defeated(u) :- in(v), att(v,u).

%% END add_Attack