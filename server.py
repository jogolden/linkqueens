#!/usr/bin/env python3

import solver
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import *
from threading import Thread

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to track solver status and result
solver_result = None
is_solver_running = False

def solve_z3_problem(board: List[List[int]]):
    global solver_result, is_solver_running

    is_solver_running = True
    
    solver_result = solver.solve_queens(board)

    is_solver_running = False

@app.post("/solve")
async def solve(board: List[List[int]]):
    global solver_result, is_solver_running
    if is_solver_running:
        return {"message": "already running"}
    
    # Reset previous result
    solver_result = None

    # Start the background thread
    thread = Thread(target=solve_z3_problem, args=(board,))
    thread.start()
    
    return {"message": "started"}

@app.get("/result")
def get_solver_result():
    if is_solver_running:
        return {"status": "pending"}
    
    if solver_result is None:
        return {"status": "not started"}
    
    return {"status": "completed", "result": solver_result}
