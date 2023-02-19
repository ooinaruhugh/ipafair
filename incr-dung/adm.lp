%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Encoding for admissible extensions
% broken apart to selectively add the parts 
% for arguments and attacks
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#program add_argument(v).
%% Guess a three values labelling. 
%% in(v) ... v is in the set
%% out(v) ... v is attacked by the set
%% undec(v) ... v is neither in the set nor attacked by the set
in(v) :- not out(v), not undec(v), arg(v).
out(v) :- not in(v), not undec(v), arg(v).
undec(v) :- not in(v), not out(v), arg(v).
#external valid_out(v).
:- out(v), not valid_out(v). % out must have one in attacker

#program add_attack(v,u).
:- in(v), in(u), att(v,u). % attacked by in must be out & attackers of in must be out
:- in(v), undec(u), att(v,u). % attacked by in must be out
:- undec(v), in(u), att(v,u). % attackers of in must be out
valid_out(u) :- in(v), att(v,u). % out must have one in attacker