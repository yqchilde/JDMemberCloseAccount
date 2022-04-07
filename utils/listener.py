import re
import sys
import json
import yaml
import psutil
import socket
from pathlib import Path
from utils.logger import Log
from func_timeout import func_set_timeout, FunctionTimedOut
# 日志
logger = Log().logger
# 获取配置
try:
    BASE_DIR = Path(__file__).resolve().parent.parent
    sms_timeout = int(
        yaml.safe_load(open(str(BASE_DIR / "config.yaml"), "r", encoding="utf-8"))["sms_captcha"]["ws_timeout"])
except:
    sms_timeout = 45

# 注意事项
_readme = """注意事项：
1. 手机端请求IP地址为监听地址，请先测试是否可以访问通
2. 用手机浏览器测试访问说明1中尝试过的IP地址，如访问通代表无问题
3. 以下IP获取到的IP仅做参考，如果全部访问不通，请检查防火墙是否开启如下端口或使用ipconfig/ifconfig查看本地其他IP
4. 记得更改手机端的请求地址，并授权软件短信权限和验证码获取权限
5. 访问测试链接后：务必关闭页面，防止浏览器一直后台请求(像：验证码一直是123456)"""


def get_inter_ip():
    """
    查询本机所有ip地址
    :return: ip
    """
    local_addrs = []
    for name, info in psutil.net_if_addrs().items():
        for addr in info:
            if socket.AddressFamily.AF_INET == addr.family:
                if addr.address == "127.0.0.1":
                    continue
                local_addrs.append(addr.address)
    return local_addrs


class SmsSocket:
    @staticmethod
    def _readme(port = 5201):
        font_color = ["\033[1;36m", "\033[0m"]
        print(
            f'{font_color[0] if sys.platform != "win32" else ""}{_readme}{font_color[1] if sys.platform != "win32" else ""}')
        for idx, val in enumerate(get_inter_ip()):
            logger.info(f"监听地址{idx + 1}:\thttp://{val}:" + str(port) + "/publish?smsCode=123456")

    def __init__(self, port = 5201):
        self.portset = port
        try:
            self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcp_server.bind(("", port))

            self.tcp_server.listen(128)
            self._readme(port)
        except OSError:
            logger.warning("请确保你没有打开另外一个监听脚本或jd_tools   ")

    @func_set_timeout(sms_timeout)
    def listener(self):
        while True:
            try:
                cs, ca = self.tcp_server.accept()
                recv_data = cs.recv(1024)
                try:
                    a = str(re.search(r'smsCode=(\d+)', str(recv_data)).group(1))
                    logger.info(f'监听到京东验证码:\t{a}')

                    return json.dumps({"sms_code": a})
                except AttributeError:
                    logger.warning(f"监听到IP: {ca[0]}访问，但未获取到短信验证码")
            except OSError:
                logger.warning("请确保你没有打开另外一个监听脚本或jd_tools")

    def get_code(self):
        try:
            return self.listener()
        except FunctionTimedOut:
            return ""

    def clean_code(self):
        cs, ca = self.tcp_server.accept()


if __name__ == '__main__':
    a = SmsSocket()
    while True:
        print(a.get_code())
