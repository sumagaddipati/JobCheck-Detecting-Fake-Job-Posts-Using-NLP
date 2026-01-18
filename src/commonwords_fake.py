from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd

df = pd.read_csv("D:/Infosys_Project/data/cleaned.csv")

fake_df = df[df["fraudulent"] == 1]["clean_text"]

vectorizer = CountVectorizer(stop_words='english', max_features=20)
bag = vectorizer.fit_transform(fake_df)

# Sum word occurrences
sum_words = bag.sum(axis=0)

words_freq = [(word, sum_words[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)

print("Top Words in Fake Job Posts:")
for word, freq in words_freq:
    print(f"{word}: {freq}")
