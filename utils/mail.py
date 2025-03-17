from datetime import datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import dotenv

dotenv.load_dotenv()

config = {
    "host": 'smtp-relay.brevo.com',
    "port": 587,
    "secure": False,
    "auth": {
        "user": os.environ.get("SMTP_USERNAME"),
        "pass": os.environ.get("SMTP_PASSWORD"),
    }
}


def send_email(body, subject="SalesDeep Products Scraping Results"):
    sender = {"name": "Shaheer", "email": "coder.shaheer@gmail.com"}
    recipients = [
        "d.kapic@hotmail.com",
        "softechops@gmail.com"
    ]

    msg = MIMEMultipart()
    msg['From'] = f"{sender['name']} <{sender['email']}>"
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(config["host"], config["port"]) as server:
            server.starttls()
            server.login(config["auth"]["user"], config["auth"]["pass"])
            server.sendmail(sender["email"], recipients, msg.as_string())
            print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")
