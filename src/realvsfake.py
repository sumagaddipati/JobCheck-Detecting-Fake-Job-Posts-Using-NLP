import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(r"D:\Infosys_Project\data\cleaned.csv")

plt.figure(figsize=(6,4))
df["fraudulent"].value_counts().plot(kind="bar", color=["green", "red"])
plt.xticks([0,1], ["Real", "Fake"])
plt.title("Distribution of Fake vs Real Job Posts")
plt.ylabel("Count")
plt.xlabel("Job Post Type")
plt.show()

