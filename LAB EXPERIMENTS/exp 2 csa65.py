import numpy as np

# Matrix A (Sales Data)
A = np.array([[10, 20],
              [30, 40]])

# Matrix B (Sales Data)
B = np.array([[5, 15],
              [25, 35]])

print("Matrix A:")
print(A)

print("\nMatrix B:")
print(B)

# Matrix Addition
print("\nAddition (A + B):")
print(A + B)

# Matrix Subtraction
print("\nSubtraction (A - B):")
print(A - B)

# Matrix Multiplication
print("\nMultiplication (A x B):")
print(np.dot(A, B))

# Transpose of Matrix A
print("\nTranspose of Matrix A:")
print(A.T)

# Inverse of Matrix A
print("\nInverse of Matrix A:")
print(np.linalg.inv(A))
