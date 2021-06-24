import os
import sys
import base64
import json
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class TuJian(object):
    """
    图鉴验证类
    图鉴打码地址：https://www.ttshitu.com
    """

    def __init__(self, _config):
        from utils.logger import Log
        self.logger = Log().logger

        self.username = _config["tj_username"]
        self.password = _config["tj_password"]

    def post_pic(self, im, type_id):
        """
        提交图片
        :return:
        """
        base64_data = base64.b64encode(im)
        b64 = base64_data.decode()
        data = {"username": self.username, "password": self.password, "typeid": type_id, "image": b64}
        ret = json.loads(requests.post("http://api.ttshitu.com/predict", json=data).text)
        if ret['success']:
            return ret["data"]
        else:
            self.logger.error(ret["message"])
            sys.exit(1)

    @staticmethod
    def report_error(pid):
        """
        提交错误图片ID
        :param pid:
        :return:
        """
        data = {"id": pid}
        ret = json.loads(requests.post("http://api.ttshitu.com/reporterror.json", json=data).text)
        if ret['success']:
            return "报错成功"
        else:
            return ret["message"]
