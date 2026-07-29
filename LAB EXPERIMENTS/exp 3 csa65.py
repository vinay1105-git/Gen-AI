import pandas as pd

data = {
    "StudentID": [101, 102, 103, 104, 105],
    "Name": ["Rahul", "Priya", "Amit", "Sneha", "Kiran"],
    "Marks": [85, 90, None, 78, 92]
}

df = pd.DataFrame(data)

print("Original Dataset:")
print(df)

print("\nMissing Values:")
print(df.isnull().sum())

df["Marks"] = df["Marks"].fillna(df["Marks"].mean())

print("\nDataset after Cleaning:")
print(df)

print("\nAverage Marks:", df["Marks"].mean())
print("Highest Marks:", df["Marks"].max())
