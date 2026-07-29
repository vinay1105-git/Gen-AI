import matplotlib.pyplot as plt

# Data
months = ["January", "February", "March", "April", "May"]
sales = [25000, 30000, 28000, 35000, 40000]

# Bar Chart
plt.figure(figsize=(6,4))
plt.bar(months, sales)
plt.title("Monthly Sales - Bar Chart")
plt.xlabel("Months")
plt.ylabel("Sales")
plt.show()

# Line Graph
plt.figure(figsize=(6,4))
plt.plot(months, sales, marker='o')
plt.title("Monthly Sales - Line Graph")
plt.xlabel("Months")
plt.ylabel("Sales")
plt.grid(True)
plt.show()
