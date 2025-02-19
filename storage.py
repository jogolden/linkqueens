#!/usr/bin/env python3

import json

class Board:
    """
    Represents a single puzzle board.
    Queens is usually a set.
    """
    def __init__(self, size, regions, queens):
        self.size = size
        self.regions = regions
        self.queens = queens

    def to_dict(self):
        """
        Convert this board into a dict suitable for JSON serialization.
        """
        return {
            "size": self.size,
            "regions": self.regions,
            # Convert set of tuples -> list of [row, col]
            "queens": [[r, c] for (r, c) in self.queens]
        }

    @staticmethod
    def from_dict(d):
        """
        Recreate a Board object from the dict created by 'to_dict'.
        """
        return Board(
            size=d["size"],
            regions=d["regions"],
            queens=set((row, col) for row, col in d["queens"])
        )

class BoardBucket:
    """
    Holds multiple Board objects.
    """
    def __init__(self):
        self.boards = []

    def add_board(self, board):
        self.boards.append(board)

    def to_list(self):
        """
        Convert all boards into a list of dicts for JSON serialization.
        """
        return [board.to_dict() for board in self.boards]
    
    def check_consistency(self):
        if len(self.boards) == 0:
            return True
        
        first = self.boards[0].size
        for b in self.boards:
            if b.size != first:
                return False
            
        return True

    @staticmethod
    def from_list(lst):
        """
        Recreate a BoardBucket from a list of board dicts.
        """
        bucket = BoardBucket()
        for bd in lst:
            bucket.add_board(Board.from_dict(bd))
        return bucket

def save_boards(bucket, filename):
    """
    Serialize all boards in 'bucket' to a JSON file.
    """
    with open(filename, "w") as fp:
        json.dump(bucket.to_list(), fp, separators=(',', ':'))

def load_boards(filename):
    """
    Load boards from a JSON file and return a BoardBucket.
    """
    with open(filename, "r") as fp:
        data = json.load(fp)
    return BoardBucket.from_list(data)
