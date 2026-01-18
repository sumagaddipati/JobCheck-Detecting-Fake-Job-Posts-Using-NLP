import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
import pickle

# Load cleaned dataset
df = pd.read_csv("data/cleaned.csv")

X = df["clean_text"]
y = df["fraudulent"]

# TF-IDF
tfidf = TfidfVectorizer(max_features=5000)
X_vec = tfidf.fit_transform(X)

# Train/Test split
X_train, X_test, y_train, y_test = train_test_split(
    X_vec, y, test_size=0.2, random_state=42
)

# All models
models = {
    "Logistic Regression": LogisticRegression(max_iter=300),
    "Naive Bayes": MultinomialNB(),
    "Random Forest": RandomForestClassifier(),

    "KNN": KNeighborsClassifier(),
}

results = {}

print("\nRunning AutoML...\n")

for name, model in models.items():
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    results[name] = acc
    print(f"{name}: {acc:.4f}")

best_model_name = max(results, key=results.get)
best_model_obj = models[best_model_name]

print("\nBest Model:", best_model_name)
print("Accuracy:", results[best_model_name])
# Save the actual model object
pickle.dump(best_model_obj, open(r"D:\\Infosys_Project\\models\\best_model.pkl", "wb"))
# Save the vectorizer used by AutoML so it can be reused
pickle.dump(tfidf, open(r"D:\\Infosys_Project\\models\\tfidf_vectorizer.pkl", "wb"))
# Save results to a JSON for downstream use
import json
with open(r"D:\\Infosys_Project\\models\\automl_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("Saved best model, vectorizer, and results.")
