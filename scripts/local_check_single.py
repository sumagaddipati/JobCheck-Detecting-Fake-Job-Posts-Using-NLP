import pickle
import json
from scipy.sparse import csr_matrix, hstack

def clean_text(t):
    import re
    t = str(t).lower()
    t = re.sub(r"http\S+|www\S+", " ", t)
    t = re.sub(r"\S+@\S+", " ", t)
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()

MODELS_DIR = "models"
logreg = pickle.load(open(MODELS_DIR+"/logistic_model.pkl","rb"))
nb = pickle.load(open(MODELS_DIR+"/naive_bayes_model.pkl","rb"))
with open(MODELS_DIR+"/keywords.json","r") as f:
    keywords = json.load(f)
tfidf = pickle.load(open(MODELS_DIR+"/tfidf_vectorizer.pkl","rb"))

s = """Urgent Hiring! Work-from-home data entry job.\nEarn ₹5,000 per day just by typing simple words.\nNo skills needed. No experience required.\nTo start your job, you must pay a security deposit of ₹1,500.\nAfter payment, your daily earnings will be activated automatically.\nLimited slots available — join now!"""

c = clean_text(s)
tfv = tfidf.transform([c])
arr = [[1 if kw in c else 0 for kw in keywords]]
kw_mat = csr_matrix(arr)
vec = hstack([tfv, kw_mat], format='csr')

lr = int(logreg.predict(vec)[0])
nb_p = int(nb.predict(vec)[0])
print('LR:', 'Fake' if lr==1 else 'Real', 'NB:', 'Fake' if nb_p==1 else 'Real')

# Also show probabilities if available (index the single-row [0,1] element)
lr_prob = float(logreg.predict_proba(vec)[0,1]) if hasattr(logreg,'predict_proba') else float(lr)
nb_prob = float(nb.predict_proba(vec)[0,1]) if hasattr(nb,'predict_proba') else float(nb_p)
print('LR prob(fake)=', lr_prob)
print('NB prob(fake)=', nb_prob)

# recommended decision by combined threshold
import json
threshold = 0.5
try:
    threshold = json.load(open(MODELS_DIR+"/model_threshold.json","r"))['combined_threshold']
except Exception:
    pass
combined = max(lr_prob, nb_prob)
print('combined_score=', combined, 'threshold=', threshold)
print('recommended=', 'Fake Job' if combined >= threshold else 'Real Job')
