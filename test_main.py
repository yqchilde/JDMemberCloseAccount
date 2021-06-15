import json
import sys
from utils.listener import WebSocket
from utils.listener import get_inter_ip


def test_websocket():
    """
    测试websocket监听验证码转发
    :return:
    """
    print("开始测试websocket监听验证码转发")
    print(f"短信验证码测试，请在手机上访问以下任一个监听地址测试连通性")
    while True:
        try:
            recv = WebSocket().listener()
            if recv != "":
                pass
        except Exception as e:
            print("测试websocket有一点小问题\n", e.args)
            sys.exit(1)


if __name__ == '__main__':
    test_websocket()
