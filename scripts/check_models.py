import pickle
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "models"

# Load models and vectorizer
logreg = pickle.load(open(MODELS_DIR / "logistic_model.pkl", "rb"))
nb = pickle.load(open(MODELS_DIR / "naive_bayes_model.pkl", "rb"))
tfidf = pickle.load(open(MODELS_DIR / "tfidf_vectorizer.pkl", "rb"))
with open(MODELS_DIR / "keywords.json", "r") as f:
    keywords = json.load(f)
from scipy.sparse import csr_matrix, hstack

try:
    scores = json.load(open(MODELS_DIR / "model_scores.json", "r"))
except Exception:
    scores = {}

print("Model scores:", scores)

# clean text function (same as app)
def clean_text(t):
    t = str(t).lower()
    t = re.sub(r"http\S+|www\S+", " ", t)
    t = re.sub(r"\S+@\S+", " ", t)
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()

# helper to make combined features for a single text
def make_feature_vector(text):
    tfv = tfidf.transform([text])
    arr = [[1 if kw in text else 0 for kw in keywords]]
    kw_mat = csr_matrix(arr)
    return hstack([tfv, kw_mat], format='csr')

samples = [
    # Fake job post
    """Congratulations! You have been shortlisted for an online work-from-home job.
    No interview required. Earn ₹50,000 per week easily.
    To activate your job account, you must pay a registration fee of ₹2,000.
    Click the link below to complete verification.
    This is a limited time offer, apply fast.""",

    # Real job post
    """We are hiring a Python Backend Developer with 2+ years of experience.
    Responsibilities include API development, database management, and cloud deployment.
    Skills required: Python, Flask, MySQL, AWS.
    Full-time role, Hyderabad location. Salary based on experience.
    Apply with your resume.""",
]

for s in samples:
    c = clean_text(s)
    vec = make_feature_vector(c)
    lr = int(logreg.predict(vec)[0])
    nb_p = int(nb.predict(vec)[0])
    print("\nSample:\n", s[:200].strip(),"...")
    print("  Logistic:\t", 'Fake' if lr==1 else 'Real')
    print("  NaiveBayes:\t", 'Fake' if nb_p==1 else 'Real')

print("\nRun `python scripts/check_models.py` to replicate local predictions.")