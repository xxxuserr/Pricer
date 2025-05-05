import smtplib
from email.message import EmailMessage

def send_email_alert(to_email, subject, body):
    EMAIL_ADDRESS = '2fb4d145ae0dab'  # username de la Mailtrap
    EMAIL_PASSWORD = '1491c84537fca7'  # înlocuiește ****fca7 cu toată parola
    SMTP_SERVER = 'sandbox.smtp.mailtrap.io'
    SMTP_PORT = 587  # poți folosi și 2525

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = 'alerta@pricer.local'  # poate fi orice în Mailtrap
    msg['To'] = to_email
    msg.set_content(body)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
