import requests

URL = "http://127.0.0.1:5000/predict"

texts = [
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
    
    # Fake Job Post 2
    """Urgent Hiring! Work-from-home data entry job.
    Earn ₹5,000 per day just by typing simple words.
    No skills needed. No experience required.
    To start your job, you must pay a security deposit of ₹1,500.
    After payment, your daily earnings will be activated automatically.
    Limited slots available — join now!""",
    
    #Real Job Post 2
    """We are looking for a Content Writer with strong English writing skills.
    Responsibilities include creating blog articles, social media content, and SEO-based website copy.
    Required skills: research ability, grammar proficiency, basic SEO knowledge.
    This is a full-time position based in Bangalore. Salary is competitive and depends on experience.
    Interested candidates can apply with their writing samples and resume."""

]

for text in texts:
    try:
        resp = requests.post(URL, json={"text": text}, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Connection error when contacting {URL}: {e}")
        print("Make sure the Flask server is running (python app.py) and reachable at http://127.0.0.1:5000")
        break

    try:
        res = resp.json()
    except ValueError:
        print('Non-JSON response:', resp.status_code, resp.text)
        continue

    print("Response:", res)