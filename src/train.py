import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report

# ------------------------------------------------------------
# Load preprocessed data (combined TF-IDF + keyword features)
# ------------------------------------------------------------
X_train = pickle.load(open(r"D:\\Infosys_Project\\models\\X_train_features.pkl", "rb"))
X_test  = pickle.load(open(r"D:\\Infosys_Project\\models\\X_test_features.pkl", "rb"))
y_train = pickle.load(open(r"D:\\Infosys_Project\\models\\y_train.pkl", "rb"))
y_test  = pickle.load(open(r"D:\\Infosys_Project\\models\\y_test.pkl", "rb"))

print("Data Loaded Successfully (features).")

# ------------------------------------------------------------
# 1️⃣ LOGISTIC REGRESSION
# ------------------------------------------------------------
log_reg = LogisticRegression(
    max_iter=3000,
    class_weight="balanced",
    n_jobs=-1
)
log_reg.fit(X_train, y_train)

y_pred_lr = log_reg.predict(X_test)

print("\n==========================")
print("LOGISTIC REGRESSION REPORT")
print("==========================")
print("Accuracy:", accuracy_score(y_test, y_pred_lr))
print(classification_report(y_test, y_pred_lr))

pickle.dump(log_reg, open(r"D:\Infosys_Project\models\logistic_model.pkl", "wb"))
print("Logistic Regression model saved!")

# ------------------------------------------------------------
# 2️⃣ NAIVE BAYES
# ------------------------------------------------------------
nb = MultinomialNB()

class_counts = y_train.value_counts().to_dict()
sample_weight = y_train.map(lambda x: 1.0 / class_counts[x]).values

nb.fit(X_train, y_train, sample_weight=sample_weight)
y_pred_nb = nb.predict(X_test)

print("\n=======================")
print("NAIVE BAYES REPORT")
print("=======================")
print("Accuracy:", accuracy_score(y_test, y_pred_nb))
print(classification_report(y_test, y_pred_nb))

pickle.dump(nb, open(r"D:\Infosys_Project\models\naive_bayes_model.pkl", "wb"))
print("Naive Bayes model saved!")

# ------------------------------------------------------------
# 3️⃣ SUPPORT VECTOR CLASSIFIER (SVC)
# ------------------------------------------------------------
# SVC removed by request; skipping training to avoid conflicting predictions.
sv = None
y_pred_sv = None

# SVC reporting and saving skipped (removed)
print("SVC reporting/skipping saved as removed.")
# ----------------------------
# Save model scores & compute combined decision threshold
# ----------------------------
from pathlib import Path
import json
import numpy as np
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix
MODELS_DIR = Path(r"D:\\Infosys_Project\\models")

scores = {
    "logistic_regression": accuracy_score(y_test, y_pred_lr),
    "naive_bayes": accuracy_score(y_test, y_pred_nb)
}

# compute per-model probabilities for class 1 (svc removed)
probs = {}
for name, model in [("logistic_regression", log_reg), ("naive_bayes", nb)]:
    if hasattr(model, "predict_proba"):
        probs[name] = model.predict_proba(X_test)[:, 1]
    else:
        probs[name] = model.predict(X_test)

combined_probas = np.vstack([probs["logistic_regression"], probs["naive_bayes"]]).max(axis=0)

# find threshold that maximizes F1 for positive class
best_t = 0.5
best_f1 = -1
for t in np.linspace(0.1, 0.9, 17):
    preds = (combined_probas >= t).astype(int)
    f1 = f1_score(y_test, preds, pos_label=1)
    if f1 > best_f1:
        best_f1 = f1
        best_t = float(t)

combined_preds = (combined_probas >= best_t).astype(int)
f1 = f1_score(y_test, combined_preds, pos_label=1)
precision = precision_score(y_test, combined_preds, pos_label=1)
recall = recall_score(y_test, combined_preds, pos_label=1)
cm = confusion_matrix(y_test, combined_preds)

with open(MODELS_DIR / "model_scores.json", "w") as f:
    json.dump(scores, f, indent=2)
with open(MODELS_DIR / "model_threshold.json", "w") as f:
    json.dump({"combined_threshold": best_t, "f1": f1, "precision": precision, "recall": recall}, f, indent=2)

# Save best model by accuracy for compatibility
best_name = max(scores, key=scores.get)
best_model = {"logistic_regression": log_reg, "naive_bayes": nb}[best_name]
pickle.dump(best_model, open(MODELS_DIR / "best_model.pkl", "wb"))

print(f"Best model: {best_name} (accuracy={scores[best_name]:.4f})")
print(f"Combined decision threshold chosen: {best_t} (F1={f1:.4f}, Precision={precision:.4f}, Recall={recall:.4f})")

# Save some false negatives for manual inspection
try:
    X_test_text = pickle.load(open(MODELS_DIR / "X_test_text.pkl", "rb"))
    fn_indices = [int(i) for i, (yt, yp) in enumerate(zip(y_test, combined_preds)) if yt == 1 and yp == 0]
    fn_samples = []
    for idx in fn_indices[:50]:
        fn_samples.append({"index": idx, "text": X_test_text.iloc[idx] if hasattr(X_test_text, 'iloc') else str(idx)})
    with open(MODELS_DIR / "false_negatives.json", "w") as f:
        json.dump(fn_samples, f, indent=2)
    print(f"Saved {len(fn_samples)} false negative examples to models/false_negatives.json")
except Exception as e:
    print("Could not save false negatives:", e)

print("Saved model scores to models/model_scores.json and best_model.pkl")