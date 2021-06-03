import asyncio
import json
import sys

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
            recv = asyncio.get_event_loop().run_until_complete(ws_conn(get_config()["ws_conn_url"]))
            if recv != "":
                sms_code = json.loads(recv)["sms_code"]
                print("发送测试验证码", sms_code)
        except Exception as e:
            print("测试websocket有一点小问题\n", e.args)
            sys.exit(1)


if __name__ == '__main__':
    test_websocket()
