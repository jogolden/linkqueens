#!/usr/bin/env python3

import argparse, storage as storage, random
from z3 import *
from tqdm import tqdm

# First generate a random "unique solution"
# Then work backwards to create the puzzle
# Use Z3 to create a valid region areas

def generate_random_queens(n):
    """
    Generate a set of n queens on an n x n board such that:
      - No two queens are in the same row or column.
      - No two queens are adjacent.
    Returns a set of (row, col) tuples.
    """
    while True:
        rows = random.sample(range(n), n)
        cols = random.sample(range(n), n)
        random.shuffle(cols)
        queens = list(zip(rows, cols))
        valid = True
        for i in range(n):
            for j in range(i + 1, n):
                r1, c1 = queens[i]
                r2, c2 = queens[j]

                # Check for adjacency.
                if abs(r1 - r2) == 1 and abs(c1 - c2) == 1:
                    valid = False
                    break

            if not valid:
                break
        if valid:
            return set(queens)

def solve_regions(stars, n):
    s = Solver()

    # Create Z3 variables:
    # regs[i][j] is the region number (0 .. nRegions-1) for cell (i,j).
    # dist[i][j] is the distance from the star in the region.
    regs = [[Int(f"r_{i}_{j}") for j in range(n)] for i in range(n)]
    dist = [[Int(f"d_{i}_{j}") for j in range(n)] for i in range(n)]

    # Constraint: Every cell's region value is between 0 and nRegions-1.
    for i in range(n):
        for j in range(n):
            s.add(And(regs[i][j] >= 0, regs[i][j] < n))

    # Constraint: Limit region area.
    # for k in range(n):
    #     s.add(Sum([If(regs[i][j] == k, 1, 0)
    #                for i in range(n) for j in range(n)]) <= max_area)

    # Constraint: Each region must contain exactly one star.
    for k in range(n):
        star_count_in_region = []
        for i in range(n):
            for j in range(n):
                if (i, j) in stars:
                    star_count_in_region.append(If(regs[i][j] == k, 1, 0))
        s.add(Sum(star_count_in_region) == 1)

    # Constraint: Regions are connected
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for i in range(n):
        for j in range(n):
            if (i, j) in stars:
                s.add(dist[i][j] == 0)
            else:
                random_dirs = dirs[:]
                random.shuffle(random_dirs)
                nbr_conditions = []
                for di, dj in random_dirs:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < n and 0 <= nj < n:
                        nbr_conditions.append(
                            And(regs[ni][nj] == regs[i][j],
                                dist[i][j] > 0,
                                dist[ni][nj] == dist[i][j] - 1
                            )
                        )
                s.add(Or(nbr_conditions))

    # Seed the regions
    # TODO: add more seeding for to increase puzzle space
    random_i = random.randint(0, n - 1)
    random_j = random.randint(0, n - 1)
    random_region = random.randint(0, n - 1)
    s.add(regs[random_i][random_j] == random_region)

    s.check()

    if s.check() == sat:
        m = s.model()
        region_solution = [[m.evaluate(regs[i][j]).as_long() for j in range(n)] for i in range(n)]
        return region_solution
    else:
        return None

# 6 is a good number to train on because it has a lot more unique solutions than 4x4 or 5x5 but not too many...
# We do not want to brute force and memorize the entire solution space in our NN!
# Few shot learning would be really interesting for this problem to look into...

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an n x n puzzle with random queens and regions.")
    parser.add_argument("output", help="Output JSON filename.")
    parser.add_argument("--puzzles", "-p", type=int, default=1, help="The number of puzzles to generate.")
    parser.add_argument("--size", "-n", type=int, default=6, help="Board size (n x n). The default is 6.")
    args = parser.parse_args()

    bb = storage.BoardBucket()

    # Generate how ever many puzzles we want
    for _ in tqdm(range(args.puzzles)):
        # Generate the random queen positions
        queens = generate_random_queens(args.size)

        # Solve for regions
        regions = solve_regions(queens, args.size)
        if regions is None:
            print("error: could not find a valid region layout!")
            continue
        
        # Add to the storage
        bb.add_board(storage.Board(args.size, regions, queens))
    
    # Save the board bucket to output file
    storage.save_boards(bb, args.output)
