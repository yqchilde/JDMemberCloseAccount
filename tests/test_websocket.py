import os
import sys
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from utils.logger import Log

logger = Log().logger


def test_websocket(_config):
    """
    测试websocket监听验证码转发
    :return:
    """
    smsSocket = SmsSocket()
    logger.info("短信验证码测试，请在手机上访问以上任一个监听地址测试连通性")
    while True:
        try:
            if _config["sms_captcha"]["jd_wstool"]:
                recv = asyncio.run(
                    ws_conn(_config["sms_captcha"]["ws_conn_url"], _config["sms_captcha"]["ws_timeout"])
                )
            else:
                recv = smsSocket.listener()
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
