import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
from pathlib import Path

# ------------------------------------------------------------
# 1️⃣ Load cleaned/merged dataset (prefer merged or cleaned_merged)
# ------------------------------------------------------------
ROOT = Path(r"D:\Infosys_Project")
candidates = [ROOT / "data" / "cleaned_merged.csv",
              ROOT / "data" / "merged.csv",
              ROOT / "data" / "cleaned.csv"]

for p in candidates:
    if p.exists():
        df = pd.read_csv(p)
        print(f"Loaded dataset: {p} -> shape {df.shape}")
        break
else:
    raise FileNotFoundError(
        "No dataset found. Expected one of: cleaned_merged.csv, merged.csv or cleaned.csv in data/"
    )

# ------------------------------------------------------------
# 2️⃣ Prepare features (X) and labels (y)
# ------------------------------------------------------------
# Ensure we have a cleaned text column; try to create if missing
if "clean_text" in df.columns:
    X = df["clean_text"]
else:
    # create a combined text column similar to clean.py if only raw text pieces exist
    text_cols = [c for c in ["title", "company_profile", "description", "requirements", "benefits"] if c in df.columns]
    if not text_cols:
        raise KeyError("No text columns found to build features. Ensure dataset contains 'clean_text' or text columns.")
    df["text"] = df[text_cols].fillna("").agg(" ".join, axis=1)
    import re
    def clean_text(t):
        t = str(t).lower()
        t = re.sub(r"http\S+|www\S+", " ", t)
        t = re.sub(r"\S+@\S+", " ", t)
        t = re.sub(r"[^a-z0-9 ]", " ", t)
        t = re.sub(r"\s+", " ", t)
        return t.strip()
    df["clean_text"] = df["text"].apply(clean_text)
    X = df["clean_text"]

y = df["fraudulent"]

# ------------------------------------------------------------
# 3️⃣ Train-test split (80% train, 20% test)
# ------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("Train size:", len(X_train))
print("Test size:", len(X_test))

# ------------------------------------------------------------
# 4️⃣ TF-IDF Vectorizer (best settings for job text)
# ------------------------------------------------------------
vectorizer = TfidfVectorizer(
    max_features=50000,
    ngram_range=(1,2),
    stop_words="english"
)

# Fit only on training data
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

print("TF-IDF shape (train):", X_train_tfidf.shape)

# ------------------------------------------------------------
# 4.1️⃣ Keyword features (binary presence of known scam indicators)
# ------------------------------------------------------------
keywords = [
    "pay", "registration", "fee", "deposit", "earn", "work-from-home",
    "work from home", "urgent", "limited", "no interview", "security",
    "apply now", "salary based", "earnings", "payment", "reward"
]

import numpy as np
from scipy.sparse import csr_matrix, hstack

# helper to create binary feature matrix for keywords
def keyword_matrix(series, kw_list):
    arr = np.zeros((len(series), len(kw_list)), dtype=int)
    for i, text in enumerate(series):
        t = str(text).lower()
        for j, kw in enumerate(kw_list):
            if kw in t:
                arr[i, j] = 1
    return csr_matrix(arr)

kw_train = keyword_matrix(X_train, keywords)
kw_test = keyword_matrix(X_test, keywords)

# stack TF-IDF and keyword features
X_train_features = hstack([X_train_tfidf, kw_train], format="csr")
X_test_features = hstack([X_test_tfidf, kw_test], format="csr")

print("Combined feature shape (train):", X_train_features.shape)

# ------------------------------------------------------------
# 5️⃣ Save processed files
# ------------------------------------------------------------

# save vectorizer
with open(r"D:\\Infosys_Project\\models\\tfidf_vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

# save transformed train/test sets (tfidf-only kept for compatibility)
pickle.dump(X_train_tfidf, open(r"D:\\Infosys_Project\\models\\X_train_tfidf.pkl", "wb"))
pickle.dump(X_test_tfidf, open(r"D:\\Infosys_Project\\models\\X_test_tfidf.pkl", "wb"))
# save combined feature matrices
pickle.dump(X_train_features, open(r"D:\\Infosys_Project\\models\\X_train_features.pkl", "wb"))
pickle.dump(X_test_features, open(r"D:\\Infosys_Project\\models\\X_test_features.pkl", "wb"))

# save labels and keywords
pickle.dump(y_train, open(r"D:\\Infosys_Project\\models\\y_train.pkl", "wb"))
pickle.dump(y_test, open(r"D:\\Infosys_Project\\models\\y_test.pkl", "wb"))
# save original train/test texts for diagnostics
pickle.dump(X_train, open(r"D:\\Infosys_Project\\models\\X_train_text.pkl", "wb"))
pickle.dump(X_test, open(r"D:\\Infosys_Project\\models\\X_test_text.pkl", "wb"))
import json
with open(r"D:\\Infosys_Project\\models\\keywords.json", "w") as f:
    json.dump(keywords, f, indent=2)

print("\nPreprocessing Completed! Files Saved Successfully.")
