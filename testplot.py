import matplotlib.pyplot as plt
import sys

print(dir(plt))
sys.exit(0)

# Sample data
x_values = [1, 2, 3, 4, 5]
y_values = [2, 4, 1, 5, 3]

# Create the plot
#plt.plot(x_values, y_values)
plt.load("gitstats/commits_by_year.plot")
# Add labels and a title
#plt.xlabel("X-axis Label")
#plt.ylabel("Y-axis Label")
#plt.title("Simple Line Plot Example")

# Save the plot to a file
#plt.savefig("simple_plot.png")

# Optionally, display the plot
plt.show()
