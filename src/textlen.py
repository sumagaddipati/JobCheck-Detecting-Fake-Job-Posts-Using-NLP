import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("D:/Infosys_Project/data/cleaned.csv")

# Create text length feature
df["text_length"] = df["clean_text"].apply(lambda x: len(str(x).split()))

print(df[["fraudulent", "text_length"]].groupby("fraudulent").mean())

# Plot distributions
plt.figure(figsize=(8,5))
df[df['fraudulent']==0]['text_length'].hist(alpha=0.5, label='Real')
df[df['fraudulent']==1]['text_length'].hist(alpha=0.5, label='Fake')
plt.xlabel("Text Length (word count)")
plt.ylabel("Number of Posts")
plt.legend()
plt.title("Distribution of Text Length for Real vs Fake Job Posts")
plt.show()
