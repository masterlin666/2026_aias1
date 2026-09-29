"""
Prerequisite Assessment — Python Problem 2: Valid Sudoku

Determine if a 9x9 Sudoku board is valid. Only the filled cells need to
be validated according to the following rules:
    1. Each row must contain the digits 1-9 without repetition.
    2. Each column must contain the digits 1-9 without repetition.
    3. Each of the nine 3x3 sub-boxes must contain the digits 1-9
       without repetition.

Note: A Sudoku board (partially filled) could be valid but is not
necessarily solvable. Only the filled cells need to be validated.

Constraints:
    - board.length == 9
    - board[i].length == 9
    - board[i][j] is a digit 1-9 or '.'

Instructions:
    - Implement the isValidSudoku method below
    - Do NOT modify the class name or method signature
"""
from typing import List


class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:
        # TODO: Implement this function
        # set for seen num
        rows = [set() for _ in range(9)]
        cols = [set() for _ in range(9)]
        boxes = [set() for _ in range(9)]

        for r in range(9):
            for c in range(9):
                val = board[r][c]
                
                # skip space
                if val == '.':
                    continue
                
                # calculate3*3
                box_idx = (r // 3) * 3 + (c // 3)
                
                # replicated?
                if (val in rows[r] or 
                    val in cols[c] or 
                    val in boxes[box_idx]):
                    return False
                
                # to the set
                rows[r].add(val)
                cols[c].add(val)
                boxes[box_idx].add(val)
                
        return True
        
