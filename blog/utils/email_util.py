import time
import os
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.encoders import encode_base64
from email.utils import formatdate

from blog.utils.utils import async_task


class _Attachment:
    def __init__(self, filename=None, content_type=None, data=None):
       self.filename = filename
       self.content_type = content_type or 'application/octet-stream'
       self.data = data


class _Message:
    def __init__(self, subject='', body='', html='', from_email='',
                 to_emails=None, cc_emails=None, bcc_emails=None,
                 attachments=None, date=None, charset='utf-8'):
        self.subject = subject
        self.body = body
        self.html = html
        self.from_email = from_email
        self.to_emails = to_emails or []
        self.cc_emails = cc_emails or []
        self.bcc_emails = bcc_emails or []
        self.attachments = attachments or []
        self.date = date or time.time()
        self.charset = charset

    def create(self):
        if len(self.attachments) == 0 and not self.html:
            msg = MIMEText(self.body, _subtype='plain', _charset=self.charset)
        elif len(self.attachments) > 0 and not self.html:
            msg = MIMEMultipart()
            msg.attach(MIMEText(self.body, _subtype='plain', _charset=self.charset))
        else:
            msg = MIMEMultipart()
            alternative = MIMEMultipart('alternative')
            alternative.attach(MIMEText(self.body, _subtype='plain', _charset=self.charset))
            alternative.attach(MIMEText(self.html, _subtype='html', _charset=self.charset))
            msg.attach(alternative)

        msg['Subject'] = Header(self.subject, self.charset)
        msg['From'] = self.from_email
        msg['To'] = '; '.join(self.to_emails)
        msg['Cc'] = '; '.join(self.cc_emails)
        msg['Date'] = formatdate(self.date, localtime=True)

        for attachment in self.attachments:
            maintype, subtype = (attachment.content_type).split('/', 1)
            f = MIMEBase(maintype, subtype)
            f.set_payload(attachment.data)
            encode_base64(f)
            f.add_header('Content-Disposition',
                         attachment.content_type,
                         filename=(self.charset, '', attachment.filename))
            msg.attach(f)

        return msg

    @property
    def recipients(self):
        recipients = list(set(self.to_emails + self.cc_emails + self.bcc_emails))
        assert len(recipients) != 0, 'No recipients have been added'
        return recipients

    def as_string(self):
        return self.create().as_string()

    def attach(self, filename, content_type, data):
        self.attachments.append(_Attachment(filename, content_type, data))

    def __str__(self):
        return self.as_string()


class Email(object):
    def __init__(self, mail_server, mail_username, mail_password, mail_port, mail_use_tls, mail_use_ssl):
        self.mail_server = mail_server or '127.0.0.1'
        self.mail_username = mail_username
        self.mail_password = mail_password
        self.mail_port = mail_port or 25
        self.use_tls = mail_use_tls or False
        self.use_ssl = mail_use_ssl or False
        self.host = None

    def __enter__(self):
        self.host = self.connect_mail_host()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if self.host:
            self.close_mail_host()

    def connect_mail_host(self):
        if self.use_ssl:
            host = smtplib.SMTP_SSL(self.mail_server, self.mail_port)
        else:
            host = smtplib.SMTP(self.mail_server, self.mail_port)

        host.set_debuglevel(1)

        if self.use_tls:
            host.starttls()
        if self.mail_username and self.mail_password:
            host.login(self.mail_username, self.mail_password)

        return host

    def close_mail_host(self):
        if self.host:
            self.host.quit()

    def send(self, message):
        assert self.host is not None, 'No email server'

        self.host.sendmail(message.from_email, message.recipients, message.as_string())


class EmailUtil:
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_USERNAME = os.environ['MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    @classmethod
    @async_task
    def send_email(cls, subject, body, from_email, to_emails,
                   cc_emails=None, bcc_emails=None, attachments=None):
        with Email(cls.MAIL_SERVER,
                   cls.MAIL_USERNAME,
                   cls.MAIL_PASSWORD,
                   cls.MAIL_PORT,
                   cls.MAIL_USE_TLS,
                   cls.MAIL_USE_SSL) as mail:
            message = _Message(subject=subject,
                               html=body,
                               from_email=from_email,
                               to_emails=to_emails,
                               cc_emails=cc_emails,
                               bcc_emails=bcc_emails,
                               charset='gb18030')
            if attachments:
                for attachment in attachments:
                    message.attach(attachment[0], 'application/octet-stream', attachment[1])
            mail.send(message)

    @classmethod
    def send_password_reset_email(cls, to_emails, nickname, password_reset_url):
        subject = '【CoCo】重设登录密码'
        body = (f'<p>您好，{nickname}：</p>'
                f'<p>您发送了重置【CoCo】登录密码的申请。'
                f'<p>请点击下面的链接进行确认，之后您将可以设置一个新密码。'
                f'<p>{password_reset_url}</p>'
                f'<p>感谢您使用CoCo</p>'
                f'<p>CoCo团队</p>')
        cls.send_email(subject, body, cls.MAIL_USERNAME, to_emails)

