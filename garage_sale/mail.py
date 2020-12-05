import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from garage_sale import app, make_g

#credentials, hardcoded is bad but whatever
EMAIL = "garagesale.na@gmail.com"
PASS = "Web Development"

#makes a single instance of a mail server that can send multiple emails
class mailSvr:
    def __init__(self):
        self.mailer = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        self.mailer.ehlo()
        self.mailer.login(EMAIL, PASS)

    def sendMail(self, address, subject, message):
        msg = MIMEMultipart()
        msg['From'] = f"Garage Sale Team <{EMAIL}>"
        msg['To'] = address
        msg['Subject'] = subject
        body = MIMEText(message, 'plain')
        msg.attach(body)

        self.mailer.sendmail(EMAIL, [address, EMAIL], msg.as_string())


@make_g
def mailer():
    return mailSvr()


