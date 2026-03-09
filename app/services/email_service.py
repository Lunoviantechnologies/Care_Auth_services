import smtplib
from email.mime.text import MIMEText

EMAIL = "gangadariprashanth12@gmail.com"
PASSWORD = "ygkgfueohyewvjip"


def send_email(to_email: str, subject: str, body: str):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL
        msg["To"] = to_email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        print("Logging in to email...")
        server.login(EMAIL, PASSWORD)

        print("Sending email...")
        server.sendmail(EMAIL, to_email, msg.as_string())

        server.quit()
        print("Email sent successfully ✅")

    except Exception as e:
        print("❌ Email Error:", str(e))