import requests
s = (
    "Urgent Hiring! Work-from-home data entry job. "
    "Earn ₹5,000 per day just by typing simple words. "
    "No skills needed. No experience required. "
    "To start your job, you must pay a security deposit of ₹1,500. "
    "After payment, your daily earnings will be activated automatically. "
    "Limited slots available — join now!"
)
try:
    r = requests.post('http://127.0.0.1:5000/predict', json={'text': s}, timeout=5)
    print('status', r.status_code)
    data = r.json()
    print('Recommended:', data.get('recommended'))
    print('Combined score:', data.get('combined_score'), 'threshold:', data.get('threshold'))
    print('LogReg:', data.get('logistic_regression'), 'prob:', data.get('logistic_prob'))
    print('NB:', data.get('naive_bayes'), 'prob:', data.get('naive_prob'))
    print('\nFull response:', data)
except Exception as e:
    print('Error:', e)
