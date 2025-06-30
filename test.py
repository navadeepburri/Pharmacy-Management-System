import smtplib
from email.mime.text import MIMEText

EMAIL_SENDER = 'nandhuburri2005@gmail.com'
EMAIL_PASSWORD = 'pxaecszitguoirvn'
EMAIL_RECEIVER = 'nandhuburri2005@gmail.com'

subject = "Test Email from Flask"
body = "This is a test to confirm the Gmail App Password works."

msg = MIMEText(body)
msg['Subject'] = subject
msg['From'] = EMAIL_SENDER
msg['To'] = EMAIL_RECEIVER

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)
    print("✅ Email sent successfully!")
except Exception as e:
    print("❌ Failed to send email:", e)
