import smtplib
from email.message import EmailMessage

def send_bulk_email(email_list, subject="Default Subject", message="Test Message"):
    # SMTP server configuration (MailHog)
    smtp_server = "localhost"
    smtp_port = 1025  # MailHog listens on port 1025 for SMTP

    # Loop through all email ids and send the email
    for email_id in email_list:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = "test@test.com"
        msg["To"] = email_id
        msg.set_content(message)

        # Sending the email using MailHog's SMTP server
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.send_message(msg)
                print(f"Email sent to {email_id}")
        except Exception as e:
            print(f"Failed to send email to {email_id}: {str(e)}")