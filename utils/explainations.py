import re

def generate_explanation(text):
    reasons = []
    risk_score = 0

    if not text or not text.strip():
        return {
            "risk": "Unknown",
            "score": 0,
            "reasons": ["No readable content found for analysis."]
        }

    t = text.lower()

    # =============================
    # 1. Unrealistic Salary Claims
    # =============================
    if re.search(r"(₹|\$)?\s*(50,?000|1\s*lakh|2\s*lakh|5\s*lakh|per\s*day|per\s*week)", t):
        reasons.append("Unrealistic or exaggerated salary claims detected.")
        risk_score += 3

    # =============================
    # 2. Guaranteed Job / No Interview
    # =============================
    if any(p in t for p in [
        "guaranteed job", "no interview", "100% placement",
        "direct offer", "no experience required"
    ]):
        reasons.append("Guarantee-based hiring language used (common in scams).")
        risk_score += 3

    # =============================
    # 3. Urgency & Pressure Tactics
    # =============================
    if any(w in t for w in [
        "urgent", "apply immediately", "limited slots",
        "last date today", "hurry up"
    ]):
        reasons.append("Urgency or pressure-based language detected.")
        risk_score += 2

    # =============================
    # 4. Personal Contact Information
    # =============================
    if re.search(r"\b\d{10}\b", t) or "whatsapp" in t or "telegram" in t:
        reasons.append("Direct personal contact details found (phone/WhatsApp).")
        risk_score += 3

    # =============================
    # 5. Personal Email Domains
    # =============================
    if any(mail in t for mail in [
        "@gmail.com", "@yahoo.com", "@outlook.com", "@hotmail.com"
    ]):
        reasons.append("Personal email domain used instead of official company email.")
        risk_score += 2

    # =============================
    # 6. Registration / Training Fees
    # =============================
    if any(p in t for p in [
        "registration fee", "training fee", "processing fee",
        "pay first", "initial deposit"
    ]):
        reasons.append("Mentions upfront payment or registration fees.")
        risk_score += 4

    # =============================
    # 7. Poor Company Information
    # =============================
    if "company details" not in t and "about us" not in t:
        reasons.append("Lack of clear company or organizational information.")
        risk_score += 1

    # =============================
    # FINAL RISK LEVEL
    # =============================
    if risk_score >= 7:
        risk = "High Risk"
    elif risk_score >= 4:
        risk = "Medium Risk"
    else:
        risk = "Low Risk"

    if not reasons:
        reasons.append("No strong scam indicators detected in the content.")

    return {
        "risk": risk,
        "score": risk_score,
        "reasons": reasons
    }
