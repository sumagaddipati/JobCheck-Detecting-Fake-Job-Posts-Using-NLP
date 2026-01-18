import requests
s = '''#° CodeAlpha Winter Internship Program — Registrations Open!
Registration Links:

1-Month Internship: https://Inkd.in/gS74_yUy @

3-Month Internship: https://Inkd.in/gg9pVj7n @

Kickstart your career with hands-on, project-based internships designed to make you
industry-ready.
Whether you're a beginner or looking to upgrade your skills, our 1-Month & 3-Month
Internship Programs offer:
& Real-world project experience
~ Internship certificate
<& Skill development with expert guidance
~ Flexible online learning
¥ Opportunity to explore 20+ domains
Why join this Winter Batch?
o® No prior experience required
® Learn at your own pace
© Build a strong portfolio for placements
Perfect for Blech, BCA, MCA, BBA, MBA & all branches.

If you're serious about building your career in tech or management—
This is the perfect place to start.

#winterinternship #reactjs #reactjsdeveloper #job #jobs #hr #hiring #jobsearch'''
try:
    r = requests.post('http://127.0.0.1:5000/predict', json={'text': s}, timeout=5)
    print('status', r.status_code)
    print(r.json())
except Exception as e:
    print('Error:', e)
