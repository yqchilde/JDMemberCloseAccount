import json
import re
import sys
import time
import threading
import socket


def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    try:
        _ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        _.connect(('1.2.3.4', 80))
        ip = _.getsockname()[0]
    finally:
        _.close()
        return ip


class MyThread(threading.Thread):
    def __init__(self, target, args=()):
        """
            因为threading类没有返回值,因此在此处重新定义MyThread类,使线程拥有返回值
        """
        super(MyThread, self).__init__()
        self.func = target
        self.args = args

    def run(self):
        # 接受返回值
        self.result = self.func(*self.args)

    def get_result(self):
        # 线程不结束,返回值为None
        try:
            return self.result
        except Exception:
            return None


def limit_decor(timeout, granularity):
    """
    timeout 最大允许执行时长, 单位:秒
    granularity 轮询间隔，间隔越短结果越精确同时cpu负载越高
    return 未超时返回被装饰函数返回值,超时则返回 None
    """

    def functions(func):
        def run(*args):
            thre_func = MyThread(target=func, args=args)
            thre_func.setDaemon(True)
            thre_func.start()
            sleep_num = int(timeout // granularity)
            for i in range(0, sleep_num):
                infor = thre_func.get_result()
                if infor:
                    return infor
                else:
                    time.sleep(granularity)
            return ""

        return run

    return functions


try:
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_server.bind(("", 5201))
    tcp_server.listen(128)
    font_color = ["\033[1;36m", "\033[0m"]
    print(f"""{font_color[0] if sys.platform != "win32" else ""}注意事项：
        1. 手机端请求IP地址为如下监听地址，请先用电脑点击一下哪个可以访问通！
        2. 用手机浏览器测试访问说明1中尝试过的IP地址，如访问通代表无问题
        3. 以下IP获取到的IP仅做参考，如果全部访问不通，请检查防火墙开启5201端口或使用ipconfig/ifconfig查看本地其他IP{font_color[1] if sys.platform != "win32" else ""}
    """)
    print(f"监听地址:\thttp://{get_host_ip()}:5201/\n其它的请 ipconfig/ifconfig 查看本地其他IP")
except:
    print("监听失败,请查看是否有同端口脚本")


# 等待时间30 轮询时间0.5
@limit_decor(30, 0.5)
def listener(*args, **kwargs):
    """
    通过 socket 监听
    """
    try:
        cs, ca = tcp_server.accept()
        recv_data = cs.recv(1024)
        a = str(re.search(r'smsCode=(\d+)', str(recv_data)).group(1))
        print(f'{time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())}\t监听到京东验证码:\t{a}')
        return json.dumps({"sms_code": a})
    except:
        return ""


if __name__ == '__main__':
    while True:
        print(listener())
