"""
Prerequisite Assessment — Python Problem 4: Grouping Student Submissions

Given a dictionary mapping file names to student names, return a
dictionary mapping each student name to a list of their submitted files.

Example:
    Input:  {'hw1_Mary.txt': 'Mary', 'hw1_Code_John.py': 'John',
             'hw1_John.txt': 'John', 'hw2_Mary.txt': 'Mary'}
    Output: {'Mary': ['hw1_Mary.txt', 'hw2_Mary.txt'],
             'John': ['hw1_Code_John.py', 'hw1_John.txt']}
    (order within each list does not matter)

Instructions:
    - Implement the group_by_students function below
    - Do NOT modify the function signature
"""



def group_by_students(files):
    result = {}
    
    for file_name, student_name in files.items():
        # 還沒出現在結果，建立一個空列表
        if student_name not in result:
            result[student_name] = []
        
        result[student_name].append(file_name)
        
    return result