# Lab 9: Structured Output Generation

def python_prompt():
    return """
Generate a Python program that accepts two numbers
and prints their sum.
Return only valid Python code.
"""

def sql_prompt():
    return """
Generate an SQL query to display the names and salaries
of employees whose salary is greater than 50000.
Table Name: Employee
Columns: EmpID, Name, Salary
Return only the SQL query.
"""

print("========== PYTHON PROMPT ==========")
print(python_prompt())

print("\n========== SQL PROMPT ==========")
print(sql_prompt())