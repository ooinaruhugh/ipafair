%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% ASP encoding for Distance-preserving graph homomorphisms
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% First, the graph homomorphism part 

edge2(W1, W2) :- edge(V1,V2), maps(V1,W1), maps(V2, W2).

% Now, we have to get hold of paths in G
