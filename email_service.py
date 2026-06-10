import smtplib

from email.mime.text import MIMEText


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

    server = smtplib.SMTP(
        "smtp.gmail.com",
        587
    )

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