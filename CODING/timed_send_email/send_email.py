import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr


class TimedSendEmail:
    """
    发送邮件
    """
    FROM_ADDR = ''  # 邮箱地址
    PASSWORD = ''   # 邮箱授权码
    SMTP_SERVER = 'smtp.qq.com'

    def __init__(self):
        pass

    def _format_addr(self, s):
        """
        对一个邮件地址进行编码。
        """
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def send_eamil(self, to_addr, header, html_str):
        try:
            msg = MIMEText(html_str, 'html', 'utf-8')
            msg['From'] = self._format_addr('凉山气象预报预警系统 管理员<' + self.FROM_ADDR + '>：')
            msg['To'] = self._format_addr(to_addr)
            msg['Subject'] = Header(header, 'utf-8').encode()
            server = smtplib.SMTP(self.SMTP_SERVER, 25)  # SMTP端口是25
            server.set_debuglevel(1)
            server.login(self.FROM_ADDR, self.PASSWORD)
            if isinstance(to_addr, list):
                to_addr = [to_addr]
            server.sendmail(self.FROM_ADDR, to_addr, msg.as_string())
            server.quit()
            return True
        except Exception as e:
            print(e)
            return False
