# -*- coding:utf-8 -*-
"""
======================================
@author:        Destiny
@file_name:     send_email.py
@create_date:   2022/6/16 13:39
@description:   Type the desc here ...
======================================
"""
import smtplib
from email.header import Header
from email.mime.text import MIMEText


class SendEmail(object):
    def __init__(self, mail_info):
        self.mail_info = mail_info

    def send_mail(self, subject, content):
        # 1.实例化SMTP
        smtp = smtplib.SMTP(self.mail_info['host'], port=587)
        # 2. 链接邮件服务器 eg:163邮箱: smtp.163.com
        # smtp.connect(self.mail_info['host'])
        smtp.connect(self.mail_info['host'], port=587)
        smtp.starttls()
        # 3. 配置发送邮箱的用户名和密码
        smtp.login(self.mail_info['from_user'], self.mail_info['from_pwd'])
        # 4. 配置发送内容msg
        msg = MIMEText(content, 'html', _charset='utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = self.mail_info['from_user']
        msg['To'] = ",".join(self.mail_info['to_user'].split(","))
        msg['Cc'] = ",".join(self.mail_info['cc_user'].split(","))
        # 5. 配置发送邮箱，接收邮箱，以及发送内容
        smtp.sendmail(self.mail_info['from_user'], (msg['To'] + ',' + msg['Cc']).split(','), msg.as_string())
        # 6. 关闭邮件服务
        smtp.quit()


if __name__ == '__main__':
    mail_info = {
        "host": "smtp.partner.outlook.cn",
        "from_user": "wei.yang@cyclone-robotics.com",
        "from_pwd": "N!WizZ5KE&",
        "to_user": "wei.yang@cyclone-robotics.com",
        "cc_user": "tangyong.zhang@cyclone-robotics.com",
        # "to_user": ["xiaotong.zhang@cyclone-robotics.com"],
        # "cc_user": ["dongkan.tao@cyclone-robotics.com"],
        "attachment_path": "",
        "attachment": "",
    }
    c = SendEmail(mail_info)
    import glob

    report_file = glob.glob('D:\\Code\\python_project\\performance_test\\report\\performance_test_report.html')[0]
    print(report_file)
    f = open(report_file, 'r', encoding='utf-8')
    html_mail = f.read()
    f.close()
    c.send_mail("RPA平台-九宫格Daily Build非功能自动化测试报告", html_mail)
