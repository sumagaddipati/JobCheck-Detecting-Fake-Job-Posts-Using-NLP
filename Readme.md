**JobShield AI – Fake Job Post Detection System**
**Project Overview**

JobShield AI is an intelligent, web-based system designed to detect fraudulent job postings using Natural Language Processing (NLP) and Machine Learning (ML).
The system analyzes job descriptions and job posters (via OCR) to classify postings as FAKE or REAL, while generating a Risk Score, Risk Level, and human-readable explanations to ensure transparency and trust.

This project is built with a strong focus on real-world applicability, Explainable AI (XAI), and secure system design, making it suitable for recruitment platforms, job portals, and fraud detection systems.

**Key Features**

Fake Job Detection using Logistic Regression

NLP-based text analysis using TF-IDF Vectorizer

OCR support for job posters using Tesseract OCR

Risk Score calculation (0–10)

Risk Level classification (Low / Medium / High)

Explainable AI – clear reasons for predictions

Role-based access control (User / Admin / Super Admin)

User & Admin Dashboards

Prediction history tracking

Secure authentication (Email & Password)

GitHub OAuth Login

OTP-based password reset via Email

Downloadable reports (CSV / PDF)

Modern and responsive UI using Tailwind CSS

**User Roles**
**User**

Submit job descriptions or job posters
I WILL

View prediction results

Understand explanations

Access personal prediction history

**Admin**

Monitor user activity

Analyze risk trends

View system-level analytics

Manage reports

**Super Admin**

Complete system control

User and admin management

Platform-level monitoring

**Technology Stack**

**Backend:** Python, Flask

**Frontend:** HTML, Tailwind CSS

**Machine Learning:**

Logistic Regression

TF-IDF Vectorizer

**OCR:** Tesseract OCR

**Database:** MySQL

**Authentication & Services:**

GitHub OAuth

Session-based Authentication

Flask-Mail (OTP Password Reset)

**Project Structure**
Infosys_Project/
├── app.py                     # **Main Flask Application**
├── db.py                      # **Database Connection Logic**
├── models/
│   ├── logistic_model.pkl     # **Trained ML Model**
│   ├── tfidf_vectorizer.pkl   # **TF-IDF Vectorizer**
│   └── keywords.json          # **Risk Indicator Keywords**
├── utils/
│   ├── explanations.py        # **Explainable AI Logic**
│   └── email_utils.py         # **OTP & Email Services**
├── templates/
│   ├── home.html
│   ├── dashboard.html
│   ├── admin_dashboard.html
│   ├── profile.html
│   ├── login.html
│   └── signup.html
├── static/                    # **CSS & Assets**
└── README.md

**How to Run the Project**

Step 1 – Clone the Repository

git clone (https://github.com/sumagaddipati/JobCheck-Detecting-Fake-Job-Posts-Using-NLP)


Step 2 – Navigate to Project Directory

cd Infosys_Project


Step 3 – Install Dependencies

pip install -r requirements.txt


Step 4 – Run the Application

python app.py


Step 5 – Open in Browser

http://127.0.0.1:5000

**Sample Output**

Result: FAKE JOB
Confidence: 90.14%
Risk Score: 9 / 10
Risk Level: High Risk

**Explanation:**

Urgency-based language detected

Direct personal contact information found

Unrealistic income claims

Missing company verification details

Author

Sumalatha Gaddipati)
Infosys Internship Project Submission
Year: 2026

Final Note ❤️

JobShield AI was developed with a strong emphasis on Explainable AI, security, and real-world deployment.
This project demonstrates how Machine Learning, NLP, and OCR can be combined to combat online recruitment fraud while maintaining clarity, trust, and usability.
