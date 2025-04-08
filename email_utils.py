# email_utils.py
import smtplib
from email.message import EmailMessage

# --- CONFIGURE YOUR SMTP ---
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_SENDER = 'your_email@gmail.com'
EMAIL_PASSWORD = 'your_app_password'  # Use env variable for production

def send_email(to_address, subject, body):
    try:
        msg = EmailMessage()
        msg['From'] = EMAIL_SENDER
        msg['To'] = to_address
        msg['Subject'] = subject
        msg.set_content(body)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        print(f"❌ Error sending email to {to_address}: {e}")
        return False
