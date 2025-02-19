#!/usr/bin/env python3

import argparse, json
from z3 import *

def solve_queens(board, state=None):
    """
    Solve a 'queens puzzle' on a board partitioned into regions using Z3.
    """

    n = len(board)
    if n == 0 or n != len(board[0]):
        return None
    
    # If state is not provided, assume all cells are empty
    if state is None:
        state = [[0 for _ in range(n)] for _ in range(n)]
    
    # Collect all region IDs
    region_ids = set()
    for i in range(n):
        for j in range(n):
            region_ids.add(board[i][j])

    # Create a Bool variable Q[i][j] indicating "Is there a queen in cell (i, j)?"
    Q = [[Bool(f"Q_{i}_{j}") for j in range(n)] for i in range(n)]

    solver = Solver()

    # 1) Respect pre-placed queens
    #    If state[i][j] == 1, Q[i][j] must be True
    for i in range(n):
        for j in range(n):
            if state[i][j] == 1:
                solver.add(Q[i][j] == True)

    # 2) Exactly one queen per region
    #    For each distinct region R, sum_{(i,j) in region R} Q[i][j] = 1
    for r in region_ids:
        cells_in_region = []
        for i in range(n):
            for j in range(n):
                if board[i][j] == r:
                    cells_in_region.append(Q[i][j])
        # sum of booleans == 1 means exactly one cell in that region is True
        solver.add(Sum(*cells_in_region) == 1)

    # 3) Row constraint: At most one queen per row
    for i in range(n):
        row_cells = [Q[i][j] for j in range(n)]
        solver.add(Sum(*row_cells) == 1)

    # 4) Column constraint: At most one queen per column
    for j in range(n):
        col_cells = [Q[i][j] for i in range(n)]
        solver.add(Sum(*col_cells) == 1)

    # 5) No two queens can be within a single cell of each other
    #    This means no adjacency in any of the 8 directions around a queen.
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]
    
    for i in range(n):
        for j in range(n):
            for di, dj in directions:
                ni, nj = i + di, j + dj

                # Check in bounds
                if 0 <= ni < n and 0 <= nj < n:
                    # Not( Q[i][j] AND Q[ni][nj] )
                    solver.add(Not(And(Q[i][j], Q[ni][nj])))

    # Check for satisfiability
    if solver.check() == sat:
        model = solver.model()
        # Build a solution grid: 1 if model says there's a queen, else 0
        solution = [[0 for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if model.evaluate(Q[i][j]):
                    solution[i][j] = 1
        return solution
    else:
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solve queens using Z3!")
    parser.add_argument("input", help="Input JSON filename containing raw board 2D array")
    parser.add_argument("--output", "-o", help="Output JSON solution to a file.")
    args = parser.parse_args()

    b = json.load(open(args.input))

    sol = solve_queens(b)
    if sol is None:
        print("no solution found!")
    else:
        print("found a solution!")
        print(sol)
        if args.output:
            json.dump(sol, open(args.output, "w"))

