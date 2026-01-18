import os
import smtplib
from email.message import EmailMessage

SMTP_HOST = os.environ.get('SMTP_HOST')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASS = os.environ.get('SMTP_PASS')
EMAIL_FROM = os.environ.get('EMAIL_FROM', SMTP_USER)
SMTP_USE_SSL = os.environ.get('SMTP_USE_SSL', '0') in ('1', 'true', 'True')
SMTP_USE_TLS = os.environ.get('SMTP_USE_TLS', '1') in ('1', 'true', 'True')


def send_email(to_email: str, subject: str, body: str, html: bool = False):
    """Send an email. If SMTP is not configured, prints to console (dev mode).

    Supports TLS (STARTTLS) and SSL (smtplib.SMTP_SSL) based on env vars:
    - SMTP_USE_SSL=1 to use SSL socket
    - SMTP_USE_TLS=1 to call starttls() (default)
    """
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        print('EMAIL (dev) ->', to_email)
        print('SUBJECT:', subject)
        print(body)
        return True

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = to_email

    if html:
        msg.set_content('This is an HTML email. Please view in an HTML-capable client.')
        msg.add_alternative(body, subtype='html')
    else:
        msg.set_content(body)

    try:
        if SMTP_USE_SSL:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as s:
                s.login(SMTP_USER, SMTP_PASS)
                s.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
                if SMTP_USE_TLS:
                    s.starttls()
                s.login(SMTP_USER, SMTP_PASS)
                s.send_message(msg)
        return True
    except Exception as e:
        print('Failed to send email', e)
        return False
