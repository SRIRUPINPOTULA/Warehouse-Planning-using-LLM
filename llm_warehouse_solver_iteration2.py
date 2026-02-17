import google.generativeai as genai
import os
import re
from pathlib import Path

# -------------------------------
# Gemini Configuration
# -------------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-pro")

# =========================================================
# STEP 1: REASONING CALIBRATION (NO OUTPUT SAVED)
# =========================================================
step1_prompt = """
You are an expert in Answer Set Programming (ASP) using Clingo.

The following examples are provided ONLY to calibrate your reasoning style.
They demonstrate correct syntax and structure for CSP encodings.

These examples are STANDALONE problems.
DO NOT assume future problems are standalone.

-----------------------------------
EXAMPLE 1: 8-Queens with Center Restriction
-----------------------------------
Problem:
Use clingo to find all solutions to the 8 queens problem such that:
- Exactly one queen per row
- No two queens share the same column
- No two queens share the same diagonal
- No queen is placed in the central 4x4 region (rows 3–6, columns 3–6)

% --------------------------------------------------
% Define the board size
% Rows and columns are numbered from 1 to 8
% --------------------------------------------------

% --------------------------------------------------
% Rule 1: Exactly one queen in each row
% For every row R (1..8), choose exactly one column C (1..8)
% such that queen(R,C) is true.
% The "1 { ... } 1" construct enforces exactly one choice.
% --------------------------------------------------
1 { queen(R,C) : C = 1..8 } 1 :- R = 1..8.

% --------------------------------------------------
% Rule 2: No two queens can be in the same column
% This is an integrity constraint (:- ...)
% If two different rows R1 and R2 have queens in the same column C,
% the solution is rejected.
% --------------------------------------------------
:- queen(R1,C), queen(R2,C), R1 != R2.

% --------------------------------------------------
% Rule 3: No two queens can be on the same diagonal
% Two queens are on the same diagonal if:
%   |row difference| == |column difference|
% If this condition holds for any pair of queens in different rows,
% the solution is invalid.
% --------------------------------------------------
:- queen(R1,C1), queen(R2,C2),
   R1 != R2,
   |R1 - R2| == |C1 - C2|.

% --------------------------------------------------
% Rule 4: No queen may be placed in the central 4x4 region
% The central region is defined as:
%   Rows 3 to 6 AND Columns 3 to 6
% Any queen placed inside this region causes the solution to be rejected.
% --------------------------------------------------
:- queen(R,C),
   R >= 3, R <= 6,
   C >= 3, C <= 6.

-----------------------------------
EXAMPLE 2: World’s Hardest Sudoku
-----------------------------------
Problem:
Solve a 9x9 Sudoku such that:
- Each number 1–9 appears exactly once per row
- Each number 1–9 appears exactly once per column
- Each number 1–9 appears exactly once per 3x3 subgrid
- Pre-filled values must be respected

% --------------------------------------------------
% Define the Sudoku grid
% Rows (R), Columns (C), and Numbers (N) range from 1 to 9
% --------------------------------------------------

% --------------------------------------------------
% Rule 1: Exactly one number per cell
% For every cell at position (R,C), choose exactly one number N (1..9).
% This guarantees that every cell is filled with one value.
% --------------------------------------------------
1 { cell(R,C,N) : N = 1..9 } 1 :- R = 1..9, C = 1..9.

% --------------------------------------------------
% Rule 2: No cell can contain two different numbers
% If a cell (R,C) is assigned two distinct numbers N1 and N2,
% the solution is invalid.
% (This rule is mostly redundant due to Rule 1, but helps clarity.)
% --------------------------------------------------
:- cell(R,C,N1), cell(R,C,N2), N1 != N2.

% --------------------------------------------------
% Rule 3: Row constraint
% Each number N must appear at most once in each row R.
% If the same number N appears in two different columns
% within the same row, the solution is rejected.
% --------------------------------------------------
:- cell(R,C1,N), cell(R,C2,N), C1 != C2.

% --------------------------------------------------
% Rule 4: Column constraint
% Each number N must appear at most once in each column C.
% If the same number N appears in two different rows
% within the same column, the solution is rejected.
% --------------------------------------------------
:- cell(R1,C,N), cell(R2,C,N), R1 != R2.

% --------------------------------------------------
% Rule 5: 3x3 subgrid constraint
% Each number N must appear at most once in each 3x3 subgrid.
%
% (R-1)/3 and (C-1)/3 compute the subgrid index (0..2).
% If two different cells belong to the same subgrid
% and contain the same number N, the solution is invalid.
% --------------------------------------------------
:- cell(R1,C1,N), cell(R2,C2,N),
   (R1-1)/3 == (R2-1)/3,
   (C1-1)/3 == (C2-1)/3,
   (R1,C1) != (R2,C2).

% --------------------------------------------------
% Pre-filled Sudoku clues
% These facts enforce the initial values of the puzzle.
% The solver must respect these assignments.
% --------------------------------------------------

cell(1,1,8).

cell(3,2,7).
cell(4,2,5).
cell(9,2,9).

cell(2,3,3).
cell(7,3,1).
cell(8,3,8).

cell(2,4,6).
cell(6,4,1).
cell(8,4,5).

cell(3,5,9).
cell(5,5,4).

cell(4,6,7).
cell(5,6,5).

cell(3,7,2).
cell(5,7,7).
cell(9,7,4).

cell(6,8,3).
cell(7,8,6).
cell(8,8,1).

cell(7,9,8).

-----------------------------------
EXAMPLE 3: Offset Sudoku
-----------------------------------
Problem:
Solve an Offset Sudoku where:
- Standard row and column constraints apply
- Each offset 3x3 block must contain numbers 1–9 exactly once
- Pre-filled values must be respected

% --------------------------------------------------
% Define the Offset Sudoku grid
% Rows (R), Columns (C), and Numbers (N) range from 1 to 9
% --------------------------------------------------

% --------------------------------------------------
% Rule 1: Exactly one number per cell
% For every cell at position (R,C), select exactly one number N (1..9).
% This ensures the grid is completely filled.
% --------------------------------------------------
1 { cell(R,C,N) : N = 1..9 } 1 :- R = 1..9, C = 1..9.

% --------------------------------------------------
% Rule 2: A cell cannot contain two different numbers
% If a single cell (R,C) is assigned two distinct numbers,
% the solution is rejected.
% (Redundant due to Rule 1, but improves readability.)
% --------------------------------------------------
:- cell(R,C,N1), cell(R,C,N2), N1 != N2.

% --------------------------------------------------
% Rule 3: Row constraint
% Each number N may appear at most once in each row R.
% If the same number appears in two different columns
% within the same row, the solution is invalid.
% --------------------------------------------------
:- cell(R,C1,N), cell(R,C2,N), C1 != C2.

% --------------------------------------------------
% Rule 4: Column constraint
% Each number N may appear at most once in each column C.
% If the same number appears in two different rows
% within the same column, the solution is rejected.
% --------------------------------------------------
:- cell(R1,C,N), cell(R2,C,N), R1 != R2.

% --------------------------------------------------
% Rule 5: Offset 3x3 block constraint
% Unlike standard Sudoku, the 3x3 blocks are "offset".
% Two cells belong to the same block if:
%   floor(R / 3) is equal AND floor(C / 3) is equal.
%
% Integer division (/) groups rows and columns differently
% compared to standard Sudoku ((R-1)/3).
% If the same number N appears twice in the same offset block,
% the solution is invalid.
% --------------------------------------------------
:- cell(R1,C1,N), cell(R2,C2,N),
   R1 / 3 == R2 / 3,
   C1 / 3 == C2 / 3,
   (R1,C1) != (R2,C2).

% --------------------------------------------------
% Pre-filled Offset Sudoku clues
% These facts define the given puzzle values.
% The solver must respect these assignments.
% --------------------------------------------------

cell(1,3,7).
cell(1,7,8).

cell(2,2,2).
cell(2,8,4).

cell(3,1,8).
cell(3,3,4).
cell(3,5,2).
cell(3,7,5).
cell(3,9,1).

cell(4,5,7).

cell(5,3,8).
cell(5,4,3).
cell(5,5,6).
cell(5,6,4).
cell(5,7,2).

cell(6,5,9).

cell(7,1,3).
cell(7,3,2).
cell(7,5,8).
cell(7,7,7).
cell(7,9,4).

cell(8,2,7).
cell(8,8,8).

cell(9,3,6).
cell(9,7,9).
"""

# Run Step 1 (calibration only)
model.generate_content(step1_prompt)

# =========================================================
# STEP 2: DOMAIN-LEVEL WAREHOUSE ENCODING (ACCURATE FOR YOUR inst.asp)
# =========================================================

inst_path = Path("inst1.asp")
inst_text = inst_path.read_text(encoding="utf-8")

inst_lines = inst_text.strip().splitlines()
inst_excerpt = "\n".join(inst_lines[:120])

step2_prompt = f"""
You are now solving a NEW problem.

-----------------------------------
IMPORTANT
-----------------------------------
You must generate a DOMAIN-LEVEL ASP ENCODING.
This encoding will be combined with DIFFERENT instance files (inst.asp).

This project uses init/2 facts with EXACT schemas as shown in the instance excerpt below.
Your domain encoding MUST work with this schema and derive ALL objects ONLY from init/2.

-----------------------------------
INSTANCE EXCERPT (SCHEMA REFERENCE)
-----------------------------------
{inst_excerpt}

-----------------------------------
STRICT RULES
-----------------------------------
1. Output ONLY valid Clingo code. No markdown. No backticks. No explanations. No comments.
2. DO NOT hardcode robots, shelves, products, grid size, orders, picking stations, highways, or actions.
3. ALL objects MUST be derived from init/2 facts.
4. DO NOT include any ground occurs(...) facts.
5. Time must be symbolic, not fixed (use #const maxT = 20 and time(0..maxT)).
6. DO NOT use arithmetic inside predicate arguments (e.g., X+DX).
7. DO NOT use tuple comparisons (e.g., (X,Y)!=(X2,Y2)).
8. DO NOT use disjunctions inside rule bodies (e.g., (a; b)).
9. Use auxiliary variables for arithmetic (e.g., NX = X + DX).
10. Use only safe variables. No undefined predicates.

-----------------------------------
MANDATORY PATTERNS
-----------------------------------
robot(R) :- init(object(robot,R),_).
shelf(S) :- init(object(shelf,S),_).
product(PR) :- init(object(product,PR),_).
pstation(P) :- init(object(pickingStation,P),_).
order(O) :- init(object(order,O),_).
node(X,Y) :- init(object(node,_), value(at,pair(X,Y))).
highway(X,Y) :- init(object(highway,_), value(at,pair(X,Y))).

Initial state examples:
at(robot,R,X,Y,0) :- init(object(robot,R), value(at,pair(X,Y))).
onfloor(S,X,Y,0) :- init(object(shelf,S), value(at,pair(X,Y))).
at(pstation,P,X,Y) :- init(object(pickingStation,P), value(at,pair(X,Y))).

Order/product facts in instances:
order_station(O,P) :- init(object(order,O), value(pickingStation,P)).
order_line(O,PR,Q) :- init(object(order,O), value(line,pair(PR,Q))).
inv(PR,S,Q) :- init(object(product,PR), value(on,pair(S,Q))).

Time:
#const maxT = 20.
time(0..maxT).
step(T) :- time(T), T < maxT.

-----------------------------------
ACTIONS
-----------------------------------
Use ONLY the following action predicates:
move(R,DX,DY,T)
pickup(R,S,T)
putdown(R,S,T)
deliver(R,S,O,P,T)

-----------------------------------
CRITICAL SEMANTIC REQUIREMENTS (READ CAREFULLY)
-----------------------------------
A) Shelf location model MUST distinguish:
   - onfloor(S,X,Y,T): shelf S placed on floor at (X,Y) at time T
   - carrying(R,S,T): robot R carries shelf S at time T
   Define derived:
   at(shelf,S,X,Y,T) :- onfloor(S,X,Y,T).
   at(shelf,S,X,Y,T) :- carrying(R,S,T), at(robot,R,X,Y,T).

B) Co-location rule:
   - Robots may share a cell with a shelf ONLY if the robot is carrying that shelf
     OR is executing pickup/putdown with that shelf at that time.
   - DO NOT forbid robot+shelf co-location after putdown in the next state.
   - Specifically: NEVER add a constraint of the form
       ':- at(robot,...), at(shelf,...), not pickup(...)'
     because it makes valid plans UNSAT.

C) Pickup/Putdown:
   - pickup(R,S,T) requires robot and shelf S be co-located AND shelf onfloor at T AND robot not already carrying.
   - putdown(R,S,T) requires carrying(R,S,T) and results in onfloor(S, robot_pos, T+1).

D) Movement:
   - move(R,DX,DY,T) only allows 4-neighborhood + wait (0,0)
   - compute NX = X + DX, NY = Y + DY with auxiliary variables
   - require node(NX,NY)

E) Collisions & swaps:
   - No two robots in same cell at same time.
   - No robot swaps positions in one timestep.
   - Ensure shelves cannot overlap each other.
   - Prevent overlapping shelves while carried as well (one shelf per robot; no shelf carried by two robots).

F) Highway restriction:
   - No shelf may be at any highway(X,Y) at ANY time, including while carried
     (because at(shelf,...) is derived from robot position when carrying).

G) Orders & delivery:
   - order_line(O,PR,Q) are requirements.
   - inv(PR,S,QINV) gives initial stock of product PR on shelf S.
   - deliver(R,S,O,P,T) allowed only if robot R is at picking station P at time T
     AND carrying(R,S,T) AND order_station(O,P).
   - A delivery with shelf S contributes product quantities for that order using inv(PR,S,QINV)
     (assume shelf inventory is not depleted across multiple deliveries; you may treat each delivery as
      delivering MIN(remaining_required, QINV) per product line on that shelf).
   - All order lines must be satisfied by time maxT.

H) Inertia:
   - Add frame axioms for at(robot,...), onfloor/4, carrying/3, and any numeric tracking you introduce.

-----------------------------------
OPTIMIZATION
-----------------------------------
Minimize makespan:
- Define goal_met(T) meaning all order lines are satisfied at time T.
- Enforce goal_met(maxT).
- Define first_goal(T) = earliest T such that goal_met(T).
- Use exactly: #minimize {{ T@1 : first_goal(T) }}.

OUTPUT ONLY CLINGO CODE.
"""

response = model.generate_content(step2_prompt)

domain_text = response.text.strip()
domain_text = re.sub(r"^```[a-zA-Z]*\s*", "", domain_text)
domain_text = re.sub(r"\s*```$", "", domain_text)

output_file = "warehouse_domain3.lp"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(domain_text.strip() + "\n")

print(f"Warehouse domain encoding written to {output_file}")
