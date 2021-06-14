import asyncio
import json
import sys
import requests
from utils.listener import listener
from utils.listener import get_host_ip
from utils.config import get_config


def test_websocket():
    """
    测试websocket监听验证码转发
    :return:
    """
    print("开始测试websocket监听验证码转发")
    while True:
        try:
            print(f"短信验证码测试，请在手机上访问{get_host_ip()}:5201/publish?smsCode=123456测试连通性")
            recv = listener()
            if recv != "":
                sms_code = json.loads(recv)["sms_code"]
                print("发送测试验证码", sms_code)
        except Exception as e:
            print("测试websocket有一点小问题\n", e.args)
            sys.exit(1)


if __name__ == '__main__':
    test_websocket()
