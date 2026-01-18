from flask import Flask, render_template, request, redirect, session, Response, flash
import pickle, json, io, re
import mysql.connector
from scipy.sparse import hstack, csr_matrix
import pytesseract
from PIL import Image
import requests
from flask_mail import Mail, Message
import random, time
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from utils.explainations import generate_explanation

from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)



# =============================
# APP CONFIG
# =============================
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "jobshield_jwt_secret_key"
jwt = JWTManager(app)
app.secret_key = "jobshield_secret"
# =============================
# GITHUB OAUTH CONFIG
# =============================
GITHUB_CLIENT_ID = "Ov23limfP95IMVIikEP9"
GITHUB_CLIENT_SECRET = "f22e986289f4ec37a7402c0242aa06be547d0ae0"

app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME="sumagaddipati@gmail.com",
    MAIL_PASSWORD="kecf wgcs gmbb vvek"
)
#MAIL_PASSWORD="kecf wgcs gmbb vvek"
mail = Mail(app)


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

#github
@app.route("/login/github")
def github_login():
    github_auth_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        "&scope=user:email"
    )
    return redirect(github_auth_url)


@app.route("/login/github/callback")
def github_callback():
    code = request.args.get("code")
    if not code:
        return redirect("/login")

    # =========================
    # 1️⃣ EXCHANGE CODE → TOKEN
    # =========================
    token_resp = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code
        }
    ).json()

    access_token = token_resp.get("access_token")
    if not access_token:
        return redirect("/login")

    # =========================
    # 2️⃣ FETCH GITHUB PROFILE
    # =========================
    user_resp = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {access_token}"}
    ).json()

    github_id = str(user_resp.get("id"))
    username = user_resp.get("login")

    # =========================
    # 3️⃣ FETCH EMAIL
    # =========================
    email_resp = requests.get(
        "https://api.github.com/user/emails",
        headers={"Authorization": f"token {access_token}"}
    ).json()

    email = None
    for e in email_resp:
        if e.get("primary") and e.get("verified"):
            email = e.get("email")
            break

    # fallback (rare case)
    if not email:
        email = f"{username}@github.com"

    # =========================
    # 4️⃣ DB LOGIC (SAFE)
    # =========================
    db = get_db()
    cur = db.cursor(dictionary=True)

    # Try by github_id
    cur.execute("SELECT * FROM users WHERE github_id=%s", (github_id,))
    user = cur.fetchone()

    # Try by email if github_id not found
    if not user:
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

    # Create new user if not exists
    if not user:
        cur.execute(
            """
            INSERT INTO users (username, email, github_id, auth_provider, role, last_login)
            VALUES (%s, %s, %s, 'GITHUB', 'USER', NOW())
            """,
            (username, email, github_id)
        )
        db.commit()

        cur.execute("SELECT * FROM users WHERE github_id=%s", (github_id,))
        user = cur.fetchone()

    # Update existing user
    else:
        cur.execute(
            """
            UPDATE users
            SET github_id=%s,
                auth_provider='GITHUB',
                last_login=NOW()
            WHERE id=%s
            """,
            (github_id, user["id"])
        )
        db.commit()

    # =========================
    # 5️⃣ LOGIN SESSION
    # =========================
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["role"] = user["role"]

    return redirect("/")



# =============================
# DATABASE
# =============================
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Suma@1321",
        database="postanalyser"
    )

# =============================
# ADMIN CHECK
# =============================
def is_admin():
    return session.get("role") in ["ADMIN", "SUPERADMIN"]

def is_superadmin():
    return session.get("role") == "SUPERADMIN"


# =============================
# LOAD MODELS
# =============================
logreg = pickle.load(open("models/logistic_model.pkl", "rb"))
nb = pickle.load(open("models/naive_bayes_model.pkl", "rb"))
tfidf = pickle.load(open("models/tfidf_vectorizer.pkl", "rb"))

with open("models/keywords.json") as f:
    keywords = json.load(f)

# =============================
# FEATURE VECTOR
# =============================
def make_feature_vector(text):
    tf = tfidf.transform([text])
    kw = [1 if k.lower() in text.lower() else 0 for k in keywords]
    return hstack([tf, csr_matrix([kw])])

# =============================
# RESULT EXPLANATION (WHY)
# =============================

# =============================
# LOGIN
# =============================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        db = get_db()
        cur = db.cursor(dictionary=True)

        cur.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (request.form["email"], request.form["password"])
        )
        user = cur.fetchone()

        if user:
            # -----------------------------
            # SESSION LOGIN (UI)
            # -----------------------------
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            # -----------------------------
            # JWT IN NORMAL FLOW
            # -----------------------------
            access_token = create_access_token(
                identity={
                    "user_id": user["id"],
                    "role": user["role"]
                }
            )
            session["jwt_token"] = access_token

            # update last login (optional but good)
            cur.execute(
                "UPDATE users SET last_login=NOW() WHERE id=%s",
                (user["id"],)
            )
            db.commit()

            return redirect("/")

        # ❌ Invalid credentials
        return render_template(
            "login.html",
            error="Invalid email or password"
        )

    # GET request → show login page
    return render_template("login.html")


@app.route("/api/jwt-check")
@jwt_required()
def jwt_check():
    user = get_jwt_identity()

    return {
        "message": "JWT access verified successfully",
        "user_id": user["user_id"],
        "role": user["role"]
    }
@app.route("/test-jwt")
def test_jwt():
    token = session.get("jwt_token")

    if not token:
        return "No JWT found. Please login first."

    return f"""
    <h3>JWT Token Found</h3>
    <textarea rows='8' cols='80'>{token}</textarea>
    <p>JWT is being generated during normal login.</p>
    """




# =============================
# SIGNUP
# =============================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        if request.form["password"] != request.form["confirm_password"]:
            return render_template("signup.html", error="Passwords do not match")

        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO users(username,email,password,role) VALUES(%s,%s,%s,'USER')",
            (request.form["username"], request.form["email"], request.form["password"])
        )
        db.commit()
        return redirect("/login")

    return render_template("signup.html")

# =============================
# LOGOUT
# =============================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


#rest password
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]

        db = get_db()
        cur = db.cursor(dictionary=True)

        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        if not user:
            flash("Email not registered", "error")
            return redirect("/forgot-password")

        otp = str(random.randint(100000, 999999))

        session["reset_email"] = email
        session["otp"] = otp
        session["otp_time"] = time.time()

        send_otp_email(email, otp)
        flash("OTP sent to your email", "success")
        return redirect("/verify-otp")

    return render_template("forgot_password.html")




def send_otp_email(email, otp):
    msg = Message(
        subject="JobShield AI – Password Reset OTP",
        sender=app.config["MAIL_USERNAME"],
        recipients=[email]
    )

    msg.html = f"""
    <div style="font-family: Arial, sans-serif; background-color:#0f172a; padding:30px;">
      <div style="max-width:500px; margin:auto; background:#020617; padding:25px; border-radius:10px; color:#e5e7eb;">
        
        <h2 style="color:#34d399; text-align:center;">JobShield AI</h2>
        <p style="font-size:14px; color:#cbd5f5;">
          You requested to reset your password.
        </p>

        <div style="margin:30px 0; text-align:center;">
          <p style="font-size:14px;">Your One-Time Password (OTP)</p>
          <div style="
              font-size:28px;
              font-weight:bold;
              letter-spacing:4px;
              color:#38bdf8;
              margin-top:10px;">
            {otp}
          </div>
        </div>

        <p style="font-size:13px; color:#94a3b8;">
          This OTP is valid for <b>10 minutes</b>.  
          Please do not share it with anyone.
        </p>

        <hr style="border:none; border-top:1px solid #1e293b; margin:20px 0;">

        <p style="font-size:12px; color:#64748b; text-align:center;">
          If you did not request this, you can safely ignore this email.<br>
          © 2026 JobShield AI
        </p>
      </div>
    </div>
    """

    mail.send(msg)




#verify otp
@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        entered_otp = request.form["otp"]

        if time.time() - session.get("otp_time", 0) > 600:
            flash("OTP expired", "error")
            return redirect("/forgot-password")

        if entered_otp == session.get("otp"):
            return redirect("/reset-password")
        else:
            flash("Invalid OTP", "error")

    return render_template("verify_otp.html")



@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        new_password = request.form["password"]
        email = session.get("reset_email")

        db = get_db()
        cur = db.cursor()

        cur.execute(
            "UPDATE users SET password=%s WHERE email=%s",
            (new_password, email)
        )
        db.commit()

        session.clear()
        flash("Password updated successfully", "success")
        return redirect("/login")

    return render_template("reset_password.html")



# =============================
# MAIN PAGE / ANALYZE (USER + ADMIN)
# =============================
@app.route("/", methods=["GET", "POST"])
def home():
    if "user_id" not in session:
        return redirect("/login")

    result = None
    confidence = None
    extracted_text = None
    prediction_id = None   # ✅ FIX

    # explanation-related
    risk_level = None
    risk_score = None
    reasons = []

    # =============================
    # TEXT ANALYSIS
    # =============================
    if request.method == "POST" and "job_text" in request.form:
        text = request.form["job_text"].strip()

        if not text:
            flash("Please enter job description before analyzing.", "error")
            return redirect("/")

        X = make_feature_vector(text)

        #lr_pred = logreg.predict(X)[0]
        start = time.time()
        lr_pred = logreg.predict(X)[0]
        end = time.time()
        prediction_time = round(end - start, 4)

        result = "FAKE JOB" if lr_pred else "REAL JOB"
        confidence = round(logreg.predict_proba(X)[0][1] * 100, 2)

        explanation = generate_explanation(text)
        risk_level = explanation["risk"]
        risk_score = explanation["score"]
        reasons = explanation["reasons"]

        db = get_db()
        cur = db.cursor()
        '''cur.execute(
            "INSERT INTO predictions (user_id, job_text, result, confidence) VALUES (%s,%s,%s,%s)",
            (session["user_id"], text, result, confidence)
        )'''
        cur.execute(
            "INSERT INTO predictions (user_id, job_text, result, confidence, response_time) VALUES (%s,%s,%s,%s,%s)",
            (session["user_id"], text, result, confidence, prediction_time)
        )

        db.commit()
        prediction_id = cur.lastrowid   # ✅ CORRECT PLACE

    # =============================
    # IMAGE ANALYSIS
    # =============================
    if request.method == "POST" and "job_image" in request.files:
        img = request.files["job_image"]

        if img.filename == "":
            flash("Please choose an image before analyzing.", "error")
            return redirect("/")

        image = Image.open(io.BytesIO(img.read()))
        extracted_text = pytesseract.image_to_string(image)

        if not extracted_text.strip():
            flash("No readable text found in the image.", "error")
            return redirect("/")

        X = make_feature_vector(extracted_text)

        lr_pred = logreg.predict(X)[0]
        result = "FAKE JOB" if lr_pred else "REAL JOB"
        confidence = round(logreg.predict_proba(X)[0][1] * 100, 2)

        explanation = generate_explanation(extracted_text)
        risk_level = explanation["risk"]
        risk_score = explanation["score"]
        reasons = explanation["reasons"]

        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO predictions (user_id, job_text, result, confidence) VALUES (%s,%s,%s,%s)",
            (session["user_id"], extracted_text, result, confidence)
        )
        db.commit()
        prediction_id = cur.lastrowid   # ✅ CORRECT

    return render_template(
        "home.html",
        result=result,
        confidence=confidence,
        risk_level=risk_level,
        risk_score=risk_score,
        reasons=reasons,
        extracted_text=extracted_text,
        prediction_id=prediction_id,
        role=session["role"],
        active="analyze"
    )
 
# =============================
# DASHBOARD (USER + ADMIN)
# =============================
"""@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cur = db.cursor(dictionary=True)

    if session["role"] == "ADMIN":
        cur.execute("SELECT COUNT(*) c FROM users")
        total_users = cur.fetchone()["c"]

        cur.execute("SELECT COUNT(*) c FROM predictions")
        total_preds = cur.fetchone()["c"]

        cur.execute("SELECT COUNT(*) c FROM predictions WHERE result='FAKE JOB'")
        fake = cur.fetchone()["c"]

        cur.execute("SELECT COUNT(*) c FROM predictions WHERE result='REAL JOB'")
        real = cur.fetchone()["c"]

        cur.execute(
            "SELECT id, username, email, role, last_login FROM users ORDER BY last_login DESC"
        )
        users = cur.fetchall()

        return render_template(
            "admin_dashboard.html",
            total_users=total_users,
            total_preds=total_preds,
            fake=fake,
            real=real,
            users=users,
            role="ADMIN",
            active="dashboard"
        )

    else:
        cur.execute(
            "SELECT COUNT(*) c FROM predictions WHERE user_id=%s",
            (session["user_id"],)
        )
        total = cur.fetchone()["c"]

        cur.execute(
            "SELECT COUNT(*) c FROM predictions WHERE user_id=%s AND result='FAKE JOB'",
            (session["user_id"],)
        )
        fake = cur.fetchone()["c"]

        return render_template(
            "dashboard.html",
            total=total,
            fake=fake,
            role="USER",
            active="dashboard"
        )"""
        
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cur = db.cursor(dictionary=True)

    # =========================
    # ADMIN / SUPERADMIN DASHBOARD
    # =========================
    if session["role"] in ["ADMIN", "SUPERADMIN"]:

        # ---- BASIC STATS ----
        cur.execute("SELECT COUNT(*) c FROM users")
        total_users = cur.fetchone()["c"]

        cur.execute("SELECT COUNT(*) c FROM predictions")
        total_preds = cur.fetchone()["c"]

        cur.execute("SELECT COUNT(*) c FROM predictions WHERE result='FAKE JOB'")
        fake = cur.fetchone()["c"]

        cur.execute("SELECT COUNT(*) c FROM predictions WHERE result='REAL JOB'")
        real = cur.fetchone()["c"]
        
        cur.execute("SELECT COUNT(*) c FROM predictions WHERE feedback='DOWN'")
        flagged = cur.fetchone()["c"]


        # ---- FEEDBACK STATS ----
        cur.execute("SELECT COUNT(*) c FROM feedback WHERE feedback='UP'")
        fb_up = cur.fetchone()["c"]

        cur.execute("SELECT COUNT(*) c FROM feedback WHERE feedback='DOWN'")
        fb_down = cur.fetchone()["c"]

        fb_total = fb_up + fb_down
        fb_accuracy = round((fb_up * 100 / fb_total), 1) if fb_total else 0

        # ---- USERS TABLE ----
        cur.execute("""
            SELECT id, username, email, role, last_login
            FROM users
            ORDER BY last_login DESC
        """)
        users = cur.fetchall()

        return render_template(
            "admin_dashboard.html",
            total_users=total_users,
            total_preds=total_preds,
            fake=fake,
            real=real,
            users=users,
            fb_up=fb_up,
            fb_down=fb_down,
            fb_accuracy=fb_accuracy,
            flagged=flagged,
            role=session["role"],
            active="dashboard"
        )

    # =========================
    # USER DASHBOARD
    # =========================
    cur.execute(
        "SELECT COUNT(*) c FROM predictions WHERE user_id=%s",
        (session["user_id"],)
    )
    total = cur.fetchone()["c"]

    cur.execute(
        "SELECT COUNT(*) c FROM predictions WHERE user_id=%s AND result='FAKE JOB'",
        (session["user_id"],)
    )
    fake = cur.fetchone()["c"]

    cur.execute(
        "SELECT COUNT(*) c FROM predictions WHERE user_id=%s AND result='REAL JOB'",
        (session["user_id"],)
    )
    real = cur.fetchone()["c"]

    return render_template(
        "dashboard.html",
        total=total,
        fake=fake,
        real=real,
        role="USER",
        active="dashboard"
    )


@app.route("/admin/retrain")
def retrain_model():
    if "user_id" not in session or session.get("role") not in ["ADMIN", "SUPERADMIN"]:
        return redirect("/login")

    db = get_db()
    cur = db.cursor(dictionary=True)

    # Count total predictions
    cur.execute("SELECT COUNT(*) c FROM predictions")
    total = cur.fetchone()["c"]

    # Count flagged predictions (thumbs down)
    cur.execute("SELECT COUNT(*) c FROM predictions WHERE feedback='DOWN'")
    flagged = cur.fetchone()["c"]

    # Store retrain log
    cur.execute("""
        INSERT INTO retrain_logs (admin_id, total_predictions, flagged_predictions)
        VALUES (%s, %s, %s)
    """, (session["user_id"], total, flagged))
    db.commit()

    flash("Model retraining pipeline executed successfully.", "success")
    return redirect("/dashboard")


@app.route("/feedback/<int:pid>/<string:value>")
def feedback(pid, value):
    if "user_id" not in session:
        return redirect("/login")

    if value not in ["UP", "DOWN"]:
        return redirect("/")

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "UPDATE predictions SET feedback=%s WHERE id=%s",
        (value, pid)
    )
    db.commit()

    flash("Feedback recorded", "success")
    return redirect("/")

#analytics of admin
@app.route("/admin/analytics")
def admin_analytics():
    if "user_id" not in session or session.get("role") not in ["ADMIN", "SUPERADMIN"]:
        return redirect("/login")

    db = get_db()
    cur = db.cursor(dictionary=True)

    # Fake vs Real
    cur.execute("SELECT COUNT(*) c FROM predictions WHERE result='FAKE JOB'")
    fake = cur.fetchone()["c"]

    cur.execute("SELECT COUNT(*) c FROM predictions WHERE result='REAL JOB'")
    real = cur.fetchone()["c"]

    # Daily prediction logs
    cur.execute("""
        SELECT DATE(created_at) as day, COUNT(*) as count
        FROM predictions
        GROUP BY DATE(created_at)
        ORDER BY day
    """)
    daily = cur.fetchall()

    days = [str(r["day"]) for r in daily]
    counts = [r["count"] for r in daily]

    return render_template(
        "admin_analytics.html",
        fake=fake,
        real=real,
        days=days,
        counts=counts,
        role=session["role"],
        active="analytics"
    )

#promote & demote
# =============================
# ADMIN: PROMOTE USER
# =============================
@app.route("/admin/promote/<int:user_id>")
def promote_user(user_id):
    if not is_superadmin():
        flash("Only Super Admin can promote users.", "error")
        return redirect("/dashboard")

    db = get_db()
    cur = db.cursor(dictionary=True)

    # fetch target user
    cur.execute("SELECT role FROM users WHERE id=%s", (user_id,))
    target = cur.fetchone()

    if not target:
        flash("User not found.", "error")
        return redirect("/dashboard")

    # only USER → ADMIN
    if target["role"] != "USER":
        flash("Only USERS can be promoted.", "info")
        return redirect("/dashboard")

    cur.execute(
        "UPDATE users SET role='ADMIN' WHERE id=%s",
        (user_id,)
    )
    db.commit()

    flash("User promoted to ADMIN.", "success")
    return redirect("/dashboard")

# =============================
# ADMIN: DEMOTE USER
# =============================

@app.route("/admin/demote/<int:user_id>")
def demote_user(user_id):

    # ONLY SUPERADMIN CAN DEMOTE
    if not is_superadmin():
        flash("Unauthorized action", "error")
        return redirect("/dashboard")

    db = get_db()
    cur = db.cursor(dictionary=True)

    # Get target user
    cur.execute("SELECT role FROM users WHERE id=%s", (user_id,))
    target = cur.fetchone()

    if not target:
        flash("User not found", "error")
        return redirect("/dashboard")

    # BLOCK SUPERADMIN DEMOTION
    if target["role"] == "SUPERADMIN":
        flash("SUPERADMIN cannot be demoted.", "error")
        return redirect("/dashboard")

    # DEMOTE ADMIN → USER
    cur.execute(
        "UPDATE users SET role='USER' WHERE id=%s",
        (user_id,)
    )
    db.commit()

    flash("User demoted successfully.", "success")
    return redirect("/dashboard")

# =============================
# PROFILE (USER ONLY)
# =============================
@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT username, email, role, last_login
        FROM users
        WHERE id=%s
    """, (session["user_id"],))

    user = cur.fetchone()

    return render_template(
        "profile.html",
        username=user["username"],
        email=user["email"],
        role=user["role"],          # USER / ADMIN / SUPERADMIN
        last_login=user["last_login"],
        active="profile"
    )


#about
@app.route("/about")
def about():
    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "about.html",
        role=session.get("role"),
        active="about"
    )

# =============================
# ADMIN: DOWNLOAD USERS CSV
# =============================
@app.route("/admin/download/users/pdf")
def download_users_pdf():

    # ONLY ADMIN / SUPERADMIN
    if "user_id" not in session or session.get("role") not in ["ADMIN", "SUPERADMIN"]:
        return redirect("/login")

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT id, username, email, role, last_login
        FROM users
        ORDER BY role DESC, last_login DESC
    """)
    users = cur.fetchall()

    if not users:
        flash("No users found.", "info")
        return redirect("/dashboard")

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # ===== HEADER =====
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(1 * inch, height - inch, "JobShield AI – Users Report")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(
        1 * inch,
        height - inch - 20,
        f"Generated by: {session.get('username')} ({session.get('role')})"
    )

    y = height - inch - 50

    # ===== TABLE HEADER =====
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(1 * inch, y, "ID")
    pdf.drawString(1.5 * inch, y, "Username")
    pdf.drawString(3.2 * inch, y, "Email")
    pdf.drawString(5.5 * inch, y, "Role")
    pdf.drawString(6.7 * inch, y, "Last Login")

    y -= 15
    pdf.setFont("Helvetica", 9)

    # ===== TABLE ROWS =====
    for u in users:

        if y < 1.2 * inch:
            pdf.showPage()
            pdf.setFont("Helvetica", 9)
            y = height - inch

        pdf.drawString(1 * inch, y, str(u["id"]))
        pdf.drawString(1.5 * inch, y, u["username"])
        pdf.drawString(3.2 * inch, y, u["email"])
        pdf.drawString(5.5 * inch, y, u["role"])
        pdf.drawString(6.7 * inch, y, str(u["last_login"] or "-"))

        y -= 14

    # ===== FOOTER =====
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.drawString(
        1 * inch,
        0.8 * inch,
        "Confidential – JobShield AI | Infosys Project"
    )

    pdf.save()
    buffer.seek(0)

    return Response(
        buffer,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=users_report.pdf"
        }
    )

@app.route("/user/download/predictions/pdf")
def download_user_predictions_pdf():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT job_text, result, confidence, created_at
        FROM predictions
        WHERE user_id=%s
        ORDER BY created_at DESC
    """, (user_id,))

    rows = cur.fetchall()

    if not rows:
        flash("No predictions available.", "info")
        return redirect("/dashboard")

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - inch
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(1 * inch, y, "JobShield AI – Prediction Report")

    y -= 30
    pdf.setFont("Helvetica", 10)

    for r in rows:
        if y < 1.5 * inch:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y = height - inch

        pdf.drawString(1 * inch, y, f"Result: {r['result']} | Confidence: {r['confidence']}%")
        y -= 15
        pdf.drawString(1 * inch, y, f"Date: {r['created_at']}")
        y -= 15
        pdf.drawString(1 * inch, y, f"Text: {r['job_text'][:100]}...")
        y -= 25

    pdf.save()
    buffer.seek(0)

    return Response(
        buffer,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment;filename=my_predictions.pdf"}
    )


#feedback
@app.route("/feedback/<int:prediction_id>/<string:fb>")
def submit_feedback(prediction_id, fb):

    if "user_id" not in session:
        return redirect("/login")

    if fb not in ["UP", "DOWN"]:
        return redirect("/")

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO feedback (user_id, prediction_id, feedback) VALUES (%s,%s,%s)",
        (session["user_id"], prediction_id, fb)
    )
    db.commit()

    flash("Feedback recorded. Thank you!", "success")
    return redirect("/")

# =============================
# RUN
# =============================
if __name__ == "__main__":
    app.run(debug=True)