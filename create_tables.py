import psycopg2

conn = psycopg2.connect(
    "postgresql://postgres:EqVvbnTdhjeittbfELJFWqslKFYAMNSs@interchange.proxy.rlwy.net:10110/railway"
)

cur = conn.cursor()

# USERS TABLE
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT DEFAULT 'USER',
    github_id TEXT,
    auth_provider TEXT,
    last_login TIMESTAMP
);
""")

# PREDICTIONS TABLE
cur.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    job_text TEXT,
    result TEXT,
    confidence FLOAT,
    response_time FLOAT,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# FEEDBACK TABLE
cur.execute("""
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    prediction_id INTEGER,
    feedback TEXT
);
""")

# RETRAIN LOG TABLE
cur.execute("""
CREATE TABLE IF NOT EXISTS retrain_log (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER,
    total_predictions INTEGER,
    flagged_predictions INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

conn.commit()
cur.close()
conn.close()

print("✅ Tables created successfully!")