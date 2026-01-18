JobShield AI – Fake Job Post Detection System

🧠 Project Description

JobShield AI is an intelligent web-based system designed to detect fraudulent job postings using Natural Language Processing (NLP) and Machine Learning.
The system analyzes job descriptions and job posters (via OCR) to classify them as FAKE or REAL, while also providing risk scores and human-readable explanations for transparency.

It supports role-based access (User, Admin, Super Admin), prediction history, dashboards, secure authentication, and data export features.

🚀 Key Features

🔍 Fake Job Detection using Logistic Regression

🧠 NLP-based text analysis with TF-IDF

🖼 OCR support for job posters (Tesseract)

📊 User & Admin Dashboards

⚠ Risk Score (0–10) and Risk Level classification

🧾 Detailed explanation for predictions (Why this result?)

👤 Role-based system:

User

Admin

Super Admin

🔐 Authentication:

Email & Password

GitHub OAuth Login

📥 Download reports (CSV / PDF)

🔁 Password reset with OTP (Email)

🎨 Modern UI using Tailwind CSS

🛠️ Technologies Used

Backend: Python, Flask

Frontend: HTML, Tailwind CSS

Machine Learning:

Logistic Regression

TF-IDF Vectorizer

OCR: Tesseract OCR

Database: MySQL

Authentication: GitHub OAuth, Session-based Auth

Email Service: Flask-Mail (OTP Reset)

📂 Project Structure (Short)
Infosys_Project/
│
├── app.py
├── db.py
├── models/
│   ├── logistic_model.pkl
│   ├── tfidf_vectorizer.pkl
│   └── keywords.json
├── utils/
│   ├── explanations.py
│   └── email_utils.py
├── templates/
│   ├── home.html
│   ├── dashboard.html
│   ├── admin_dashboard.html
│   ├── profile.html
│   ├── login.html
│   └── signup.html
├── static/
└── README.md

▶️ How to Run the Project
# Clone the repository
git clone <YOUR_GITHUB_REPO_LINK>

# Navigate to project
cd Infosys_Project

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py


Access the app at:

http://127.0.0.1:5000

📊 Output Example

Result: FAKE JOB

Confidence: 90.14%

Risk Score: 9 / 10

Risk Level: High Risk

Explanation:

Urgency-based language detected

Direct personal contact information found

Unrealistic income claims

Missing company verification details

👨‍💻 Author

Tony (Sumagaddipati)
Final Year Project – Infosys Internship Submission
2026

🏁 Final Note (You can add this line ❤️)

This project was developed with a focus on real-world applicability, explainability, and secure system design, making it suitable for deployment in recruitment platforms and fraud detection systems.
