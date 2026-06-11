import smtplib

from email.mime.text import MIMEText

print("STARTING EMAIL SEND")

 

def send_notification_email(
    to_email,
    company,
    subject
):

    sender_email = "message.bytdata@gmail.com"

    app_password = "vkyhddgxnbxmoxdi"

    body = f"""
🚨 New Customer Ticket

Company: {company}

Subject: {subject}

Please login to ByteData app.
"""

    msg = MIMEText(body)

    msg["Subject"] = f"Urgent! Bytedata - {company}"

    msg["From"] = sender_email

    msg["To"] = to_email

    print("CONNECTING TO GMAIL")

    server = smtplib.SMTP(
        "smtp.gmail.com",
        587,
        timeout=15

    )

    print("GMAIL LOGIN SUCCESS")

    server.starttls()

    server.login(
        sender_email,
        app_password
    )

    server.sendmail(
        sender_email,
        to_email,
        msg.as_string()
    )

    server.quit()

    print(
        f"Email Sent To {to_email}"
    )

    print("EMAIL SENT")