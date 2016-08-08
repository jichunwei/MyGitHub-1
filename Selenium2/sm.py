# coding:utf-8

import smtplib
from email.mime.text import MIMEText
from email.header import Header

fb = open('D:/workspace/Selenium2/Unit/TestReport/2016-04-04_12-08-32result.html', 'rb')
mail_body = fb.read()
print mail_body
fb.close()

msg = MIMEText(mail_body, 'html', 'utf-8')
# msg = MIMEText(mail_body, 'html', 'utf-8')
msg['Subject'] = Header('报告', 'utf-8')


smtp = smtplib.SMTP()
smtp.connect('smtp.sina.com')
smtp.login('tan_tsx@sina.com', 'tsx,871024')
smtp.sendmail('tan_tsx@sina.com', 'tan_tsx@163.com', msg.as_string())
smtp.quit()