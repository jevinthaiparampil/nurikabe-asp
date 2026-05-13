% Source: Honu08/Nurikabe (Texas Tech, Omar Rodriguez Santiago / Dr. Richard Watson)
%         https://github.com/Honu08/Nurikabe
% Input:  rows(R). cols(C). clue(R,C,N).
% Output: white(R,C). black(R,C).

cell(R,C) :- R = 1..Rows, C = 1..Cols, rows(Rows), cols(Cols).

{ white(R,C) } :- cell(R,C).

:- not white(R,C), clue(R,C,_).

black(R,C) :- cell(R,C), not white(R,C).

adj(R,C,R1,C1) :- cell(R,C), cell(R1,C1), |R-R1| + |C-C1| == 1.

connected(w,R,C,R,C) :- white(R,C).
connected(b,R,C,R,C) :- black(R,C).
connected(w,R,C,U,V) :- connected(w,R,C,W,Z), adj(W,Z,U,V), white(U,V).
connected(b,R,C,U,V) :- connected(b,R,C,W,Z), adj(W,Z,U,V), black(U,V).

w_connected(R,C) :- connected(w,R,C,U,V), white(R,C), clue(U,V,_).
:- white(R,C), not w_connected(R,C).

:- clue(R,C,_), clue(U,V,_), R < U, connected(w,R,C,U,V).
:- clue(R,C,_), clue(U,V,_), R == U, C < V, connected(w,R,C,U,V).

island(R,C) :- N { connected(w,R,C,U,V) : cell(U,V) } N, clue(R,C,N).
:- clue(R,C,_), not island(R,C).

:- black(R,C), black(U,V), not connected(b,R,C,U,V).

:- black(R,C), black(R,C+1), black(R+1,C), black(R+1,C+1).

#show white/2.
#show black/2.
