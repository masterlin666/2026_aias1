"""
Prerequisite Assessment — Python Problem 5: Select Specific Elements

Given a 2D numpy array and a list of (row, col) index tuples, return a
1D numpy array of the elements at those positions.

Example:
    arr = [[1,2,3],[4,5,6],[7,8,9]], indices = [(0,1),(1,1),(2,0)]
    Output: [2, 5, 7]

Instructions:
    - Implement the select_elements function below
    - Do NOT modify the function signature
    - You must use numpy
"""

import numpy as np

def select_elements(arr, indices):
    arr = np.array(arr)
    if not indices:
        return np.array([])
    rows, cols = zip(*indices)
    return arr[list(rows), list(cols)]