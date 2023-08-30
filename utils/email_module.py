import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Fetch email settings from .env
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
RECIPIENT_EMAILS = os.getenv('RECIPIENT_EMAILS').split(",")  # Assuming emails are comma-separated in .env


def send_email(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAILS

    # Send the email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
