# coding:utf-8
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import os
from email.mime.multipart import MIMEMultipart

# 发送邮箱服务器
smtpserver = 'smtp.sina.com'

# 发送邮箱用户/密码
username = 'tan_tsx@sina.com'
password = 'tsx,871024'
# 发送邮箱
sender = 'tan_tsx@sina.com'
# 接收邮箱
receiver = 'tan_tsx@163.com'
# 发送邮件主题
subject = 'Python email test'

# 编写HTML类型的邮件正文
msg = MIMEText('<html><h1>Hello! </h1></html>', 'html', 'utf-8')
msg['Subject'] = Header(subject, 'utf-8')

# 发送附件
sendfile = open('D:\workspace\Selenium2\Unit\TestReport\log.txt', 'rb').read()

att = MIMEText(sendfile, 'base64', 'utf-8')
att['Content-Ttpe'] = 'application/octet-stream'
att['Content-Disposition'] = 'attachment'; filename='log.txt'

msgRoot = MIMEMultipart('related')
msgRoot.attach(att)

# 链接发送邮件
smtp = smtplib.SMTP()
smtp.connect(smtpserver)
smtp.login(username, password)
smtp.sendmail(sender, receiver, msg.as_string())
smtp.quit()
