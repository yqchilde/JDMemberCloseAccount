import os
import random
import sys
import re
import time
import requests
from hashlib import md5

baidu_api = "http://api.fanyi.baidu.com/api/trans/sdk/picture"
sms_code = ""
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class BaiduFanYi(object):
    """
    百度翻译识别类，用于帮助ios设备识别投屏后的短信验证码
    """

    def __init__(self, _config, debug=False):
        from utils.logger import Log
        self.logger = Log().logger
        self.app_id = _config["baidu_fanyi_appid"]
        self.app_key = _config["baidu_fanyi_appkey"]
        self.debug = debug
        if self.app_id == "" or self.app_key == "":
            self.logger.warning("请在config.yaml中配置baidu翻译相关配置")
            sys.exit(1)

    @staticmethod
    def get_file_md5(file):
        return md5(file).hexdigest()

    def baidu_fanyi(self, _range_, delay_time=5):
        """
        百度ocr识别数字
        :param delay_time: ocr识别延迟时间
        :param _range_: 验证码截图区域坐标(左x,左y,右x,右y)
        :ocr_return: 识别到的数字
        """
        global sms_code
        screenshot_save(_range_)
        img = open(captcha_screenshot, 'rb').read()

        salt = random.randint(32768, 65536)
        sign = md5(
            (self.app_id + self.get_file_md5(img) + str(salt) + "APICUID" + "mac" + self.app_key).encode("utf-8")
        ).hexdigest(),
        payload = {
            "from": "zh",
            "to": "zh",
            "appid": self.app_id,
            "salt": salt,
            "sign": sign,
            "cuid": "APICUID",
            "mac": "mac"
        }
        image = {
            "image": (os.path.basename(captcha_screenshot), img, "multipart/form-data")
        }
        ocr_ret = requests.post(baidu_api, params=payload, files=image).json()

        # debug模式打印识别内容
        if self.debug:
            self.logger.info(ocr_ret)

        if ocr_ret["error_code"] == "0":
            ocr_ret = ocr_ret["data"]
            if ocr_ret["sumSrc"] == "":
                self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
                time.sleep(delay_time)
                return self.baidu_fanyi(_range_, delay_time)

            fan_yi_ocr_ret = str(ocr_ret["sumSrc"])
            find_all = ""
            for rule in matching_rules:
                find_all = re.findall(rule, fan_yi_ocr_ret)
                if len(find_all) >= 1:
                    break

            if len(find_all) == 1:
                code = find_all[0].strip("'")
                if sms_code == code:
                    self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
                    time.sleep(delay_time)
                    return self.baidu_fanyi(_range_, delay_time)
                else:
                    sms_code = code

                return code
            else:
                self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
                time.sleep(delay_time)
                return self.baidu_fanyi(_range_, delay_time)
        else:
            self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
            time.sleep(delay_time)
            return self.baidu_fanyi(_range_, delay_time)


if __name__ == '__main__':
    from utils.config import get_config

    ocr_cfg = get_config("../config.yaml")["sms_captcha"]["ocr"]
    _range_ = ocr_cfg["ocr_range"]
    sms_code = BaiduFanYi(ocr_cfg, True).baidu_fanyi(_range_, ocr_cfg["ocr_delay_time"])
    print("百度翻译识别到的验证码是：", sms_code)
else:
    from captcha.config import *
