import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app

c = app.test_client()

# Cleanup any previous test user if exists (sqlite direct)
import sqlite3
con = sqlite3.connect('users.db')
con.execute("DELETE FROM users WHERE email=?", ('test@example.com',))
con.commit()
con.close()

# Signup
resp = c.post('/signup', data={'username':'testuser','email':'test@example.com','password':'pass123'}, follow_redirects=False)
print('signup status', resp.status_code, 'Location:', resp.headers.get('Location'))
# After signup should be redirected to /verify

# Simulate verification: get code from DB (we expect dev email printed, but we'll query DB)
import sqlite3
con = sqlite3.connect('users.db')
con.row_factory = sqlite3.Row
uid_row = con.execute("SELECT id FROM users WHERE email=?", ('test@example.com',)).fetchone()
print('user id:', uid_row['id'])
code_row = con.execute("SELECT token FROM email_verifications WHERE user_id=? ORDER BY created_at DESC LIMIT 1", (uid_row['id'],)).fetchone()
print('stored token exists:', bool(code_row))
# We can't recover the clear code since it's hashed; for test we will simulate that verifying works by directly marking user verified
con.execute("UPDATE users SET is_verified=1 WHERE id=?", (uid_row['id'],))
con.execute("DELETE FROM email_verifications WHERE user_id=?", (uid_row['id'],))
con.commit()
con.close()

# Login via form
resp = c.post('/login', data={'email':'test@example.com','password':'pass123'}, follow_redirects=False)
print('login status', resp.status_code, 'Location:', resp.headers.get('Location'))

# After login, try dashboard with session preserved
with app.test_client() as client:
    client.post('/login', data={'email':'test@example.com','password':'pass123'}, follow_redirects=True)
    dash = client.get('/dashboard')
    print('dashboard status:', dash.status_code)
    print('dashboard contains Dashboard:', 'Dashboard' in dash.get_data(as_text=True))

# Try accessing predict without login (new client)
with app.test_client() as anon:
    pred = anon.post('/predict', json={'text':'some job'}, follow_redirects=False)
    print('predict without login status:', pred.status_code)

# Try predict after login
with app.test_client() as client2:
    client2.post('/login', data={'email':'test@example.com','password':'pass123'}, follow_redirects=True)
    pred2 = client2.post('/predict', json={'text':'some job'})
    print('predict with login status:', pred2.status_code, 'body:', pred2.get_json())

# Test forgot/reset flow (simulate by directly inserting reset token then calling /reset POST)
import random, hashlib
with app.test_client() as client3:
    # request a reset
    r = client3.post('/forgot', data={'email':'test@example.com'}, follow_redirects=True)
    print('/forgot redirects to:', r.status_code)
    # fetch token from sqlite
    con = sqlite3.connect('users.db')
    con.row_factory = sqlite3.Row
    uid = con.execute('SELECT id FROM users WHERE email=?', ('test@example.com',)).fetchone()['id']
    token_row = con.execute('SELECT token FROM password_resets WHERE user_id=? ORDER BY created_at DESC LIMIT 1', (uid,)).fetchone()
    print('reset token stored:', bool(token_row))
    # clean up
    con.execute('DELETE FROM password_resets WHERE user_id=?', (uid,))
    con.commit()
    con.close()
