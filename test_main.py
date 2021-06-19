import sys
import asyncio

from utils.listener import WebSocket
from main import ws_conn
from utils.config import get_config


def test_websocket():
    """
    测试websocket监听验证码转发
    :return:
    """
    print("开始测试websocket监听验证码转发")
    while True:
        try:
            if get_config()["sms_captcha"]["jd_wstool"]:
                recv = asyncio.get_event_loop().run_until_complete(ws_conn(get_config()["sms_captcha"]["ws_conn_url"]))
            else:
                print(f"短信验证码测试，请在手机上访问以下任一个监听地址测试连通性")
                recv = WebSocket().listener()
            if recv != "":
                pass
        except Exception as e:
            print("测试websocket有一点小问题\n", e.args)
            sys.exit(1)


if __name__ == '__main__':
    test_websocket()
