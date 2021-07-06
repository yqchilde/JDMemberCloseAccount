import os
import sys
import asyncio


def test_websocket(_config):
    """
    测试websocket监听验证码转发
    :return:
    """
    print("开始测试websocket监听验证码转发")
    while True:
        try:
            if _config["sms_captcha"]["jd_wstool"]:
                recv = asyncio.get_event_loop().run_until_complete(
                    ws_conn(_config["sms_captcha"]["ws_conn_url"], _config["sms_captcha"]["ws_timeout"])
                )
            else:
                print(f"短信验证码测试，请在手机上访问以下任一个监听地址测试连通性")
                recv = SmsSocket().listener()
            if recv != "":
                pass
        except Exception as e:
            print("测试websocket有一点小问题\n", e.args)
            if _config["debug"]:
                import traceback
                traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    from utils.config import get_config
    from utils.listener import SmsSocket
    from main import ws_conn

    _config = get_config("../config.yaml")

    test_websocket(_config)
