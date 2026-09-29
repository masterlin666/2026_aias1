"""
Prerequisite Assessment — Python Problem 6: Euclidean Distance

Calculate the Euclidean distance between two points in N-dimensional
space using numpy.

Example:
    point1 = [1, 2, 3], point2 = [4, 5, 6]
    Output: 5.196152422706632

Instructions:
    - Implement the euclidean_distance function below
    - Do NOT modify the function signature
    - You must use numpy
"""
import numpy as np


def euclidean_distance(point1, point2):
    p1 = np.array(point1)
    p2 = np.array(point2)
    
    distance = np.sqrt(np.sum((p1 - p2)**2))
    return distance
