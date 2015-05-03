
from email import Encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename
import smtplib


def notify_by_mail(subject, text, files=None):
    me = "efmp.migulu@gmail.com"
    me_passwd="27328703ef"
    you =['pon.nieh@gmail.com',]
    
    msg = MIMEMultipart()
    msg['Subject']=subject
    msg['From']=me
    msg['To']=', '.join(you)
    for f in files or []:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(f, "rb").read())
        Encoders.encode_base64(part)
    
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % basename(f))
    
        msg.attach(part)
    if text:
        msg.attach(MIMEText(text, 'plain', 'UTF-8'))
    smtpserver = smtplib.SMTP("smtp.gmail.com",587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(me, me_passwd)
    
    smtpserver.sendmail(me, you, msg.as_string())
    smtpserver.close()
    
