% Source: Honu08/Nurikabe (Texas Tech, Omar Rodriguez Santiago / Dr. Richard Watson)
%         https://github.com/Honu08/Nurikabe
% Input:  rows(R). cols(C). clue(R,C,N).
% Output: white(R,C). black(R,C).

% Instantiate the grid
cell(R,C) :- R = 1..Rows, C = 1..Cols, rows(Rows), cols(Cols).

% Guess which cells are white
{ white(R,C) } :- cell(R,C).

% Clue cells must be white
:- not white(R,C), clue(R,C,_).

% Every non-white cell is black
black(R,C) :- cell(R,C), not white(R,C).

% Orthogonal adjacency
adj(R,C,R1,C1) :- cell(R,C), cell(R1,C1), |R-R1| + |C-C1| == 1.

% Connectivity (reachability) for white and black cells
connected(w,R,C,R,C) :- white(R,C).
connected(b,R,C,R,C) :- black(R,C).
connected(w,R,C,U,V) :- connected(w,R,C,W,Z), adj(W,Z,U,V), white(U,V).
connected(b,R,C,U,V) :- connected(b,R,C,W,Z), adj(W,Z,U,V), black(U,V).

% Every white cell must reach a clue
w_connected(R,C) :- connected(w,R,C,U,V), white(R,C), clue(U,V,_).
:- white(R,C), not w_connected(R,C).

% No two clue cells in the same white region
:- clue(R,C,_), clue(U,V,_), R < U, connected(w,R,C,U,V).
:- clue(R,C,_), clue(U,V,_), R == U, C < V, connected(w,R,C,U,V).

% Each island's size must equal its clue number
island(R,C) :- N { connected(w,R,C,U,V) : cell(U,V) } N, clue(R,C,N).
:- clue(R,C,_), not island(R,C).

% All black cells form one connected region (the sea)
:- black(R,C), black(U,V), not connected(b,R,C,U,V).

% No 2x2 block of black cells
:- black(R,C), black(R,C+1), black(R+1,C), black(R+1,C+1).

% Output
#show white/2.
#show black/2.
