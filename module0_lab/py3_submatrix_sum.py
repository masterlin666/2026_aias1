"""
Prerequisite Assessment — Python Problem 3: 4x4 Submatrix Sum

Given a 4x4 two-dimensional list (matrix) and a target sum, check if the
sum of elements in each 2x2 sub-matrix equals the target sum. Return True
if all sub-matrices meet the target sum, otherwise False.

The submatrix check includes ALL possible 2x2 sub-matrices (9 total for
a 4x4 matrix).

Example:
    matrix = [[1,2,1,2],[2,1,2,1],[1,2,1,2],[2,1,2,1]], target_sum = 6
    Output: True  (every 2x2 sub-matrix sums to 6)

Instructions:
    - Implement the validate_submatrix_sum function below
    - Do NOT modify the function signature
"""

def validate_submatrix_sum(matrix, target_sum):
    for r in range(3):
        for c in range(3):
            current_sum = (
                matrix[r][c] + matrix[r][c+1] + 
                matrix[r+1][c] + matrix[r+1][c+1]
            )
            
            # return False if any 2x2 sub-matrix does not equal target_sum
            if current_sum != target_sum:
                return False
    return True