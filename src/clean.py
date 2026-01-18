import pandas as pd
import re
from pathlib import Path

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
ROOT = Path(r"D:\Infosys_Project")
# Prefer merged dataset if available (merged.csv created by merge.py)
in_candidates = [ROOT / "data" / "merged.csv",
                 ROOT / "data" / "fake_job_postings.csv"]
INPATH = None
for p in in_candidates:
    if p.exists():
        INPATH = p
        break
if INPATH is None:
    raise FileNotFoundError("No input CSV found. Expected 'merged.csv' or 'fake_job_postings.csv' in data/")

# If we're processing merged.csv produce cleaned_merged.csv, otherwise cleaned.csv
OUTPATH = ROOT / "data" / ("cleaned_merged.csv" if INPATH.name == "merged.csv" else "cleaned.csv")

print("Loading merged dataset...")
df = pd.read_csv(INPATH)
print("Initial shape:", df.shape)
print("Before Cleaning:",df.head())
# ------------------------------------------------------------
# 1️⃣ Remove duplicates
# ------------------------------------------------------------
df = df.drop_duplicates()
print("After dropping duplicates:", df.shape)

# ------------------------------------------------------------
# 2️⃣ Ensure important text columns exist and fill missing values
# ------------------------------------------------------------
text_columns = ["title", "company_profile", "description", "requirements", "benefits"]

for col in text_columns:
    if col not in df.columns:
        df[col] = ""
    else:
        df[col] = df[col].fillna("")

# ------------------------------------------------------------
# 3️⃣ Combine text columns into a single text field
# ------------------------------------------------------------
df["text"] = (
    df["title"] + " " +
    df["company_profile"] + " " +
    df["description"] + " " +
    df["requirements"] + " " +
    df["benefits"]
)

print("Combined text column created.")

# ------------------------------------------------------------
# 4️⃣ Cleaning Function
# ------------------------------------------------------------
def clean_text(t):
    t = t.lower()
    t = re.sub(r"http\S+|www\S+", " ", t)  # remove URLs
    t = re.sub(r"\S+@\S+", " ", t)         # remove emails
    t = re.sub(r"[^a-z0-9 ]", " ", t)      # keep only alphanumeric
    t = re.sub(r"\s+", " ", t)             # remove extra spaces
    return t.strip()

print(f"Cleaning text from {INPATH.name}... This may take some time.")
df["clean_text"] = df["text"].apply(clean_text)

# ------------------------------------------------------------
# 5️⃣ Remove rows with empty clean_text (Optional)
# ------------------------------------------------------------
before = df.shape[0]
df = df[df["clean_text"].str.len() > 2]
removed = before - df.shape[0]
print(f"Removed {removed} empty or tiny text rows.")
print("After Cleaning:",df.head())

# ------------------------------------------------------------
# 6️⃣ Save cleaned dataset
# ------------------------------------------------------------
OUTPATH.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPATH, index=False)

print("Cleaning complete!")
print("Final cleaned shape:", df.shape)
print("Saved cleaned dataset at:", OUTPATH)

# Show fraud count
print("\nFraudulent counts after cleaning:")
print(df["fraudulent"].value_counts())
