import requests
URL = "http://127.0.0.1:5000/predict"
try:
    r = requests.post(URL, json={"text":"hello test"}, timeout=5)
    print('status:', r.status_code)
    print('body:', r.text)
except Exception as e:
    print('error:', e)
