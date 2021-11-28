import os
import random
import sys
import re
import time
import requests
from hashlib import md5
from PIL import ImageGrab

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
    def get_code_pic(_range, name='ios_code_pic.png'):
        """
        获取验证码图像
        :param _range:
        :param name:
        :return:
        """

        # 确定验证码的左上角和右下角坐标
        code_pic = ImageGrab.grab(_range)
        code_pic.save(name)
        return code_pic

    @staticmethod
    def get_file_md5(file):
        return md5(file).hexdigest()

    def baidu_fanyi(self, _range, delay_time=5):
        """
        百度ocr识别数字
        :param delay_time: ocr识别延迟时间
        :param _range: 验证码截图区域坐标(左x,左y,右x,右y)
        :return: 识别到的数字
        """
        global sms_code
        self.get_code_pic(_range)
        img = open('ios_code_pic.png', 'rb').read()

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
            "image": (os.path.basename("ios_code_pic.png"), img, "multipart/form-data")
        }
        ret = requests.post(baidu_api, params=payload, files=image).json()

        # debug模式打印识别内容
        if self.debug:
            self.logger.info(ret)

        if ret["error_code"] == "0":
            ret = ret["data"]
            if ret["sumSrc"] == "":
                self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
                time.sleep(delay_time)
                return self.baidu_fanyi(_range, delay_time)

            fan_yi_ret = str(ret["sumSrc"])
            find_all = re.findall(r'\'[\d]{6}\'', fan_yi_ret)
            if len(find_all) != 1:
                find_all = re.findall(r'([\d]{6})[\u3002]', fan_yi_ret)
            if len(find_all) != 1:
                find_all = re.findall(r'(您的验证码为[\d]{6})', fan_yi_ret)

            if len(find_all) == 1:
                code = find_all[0].strip("'")
                if sms_code == code:
                    self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
                    time.sleep(delay_time)
                    return self.baidu_fanyi(_range, delay_time)
                else:
                    sms_code = code

                return code
            else:
                self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
                time.sleep(delay_time)
                return self.baidu_fanyi(_range, delay_time)
        else:
            self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
            time.sleep(delay_time)
            return self.baidu_fanyi(_range, delay_time)


if __name__ == '__main__':
    from utils.config import get_config

    ocr_cfg = get_config("../config.yaml")["sms_captcha"]["ocr"]
    _range = ocr_cfg["ocr_range"]
    sms_code = BaiduFanYi(ocr_cfg).baidu_fanyi(_range, ocr_cfg["ocr_delay_time"])
    print("百度翻译识别到的验证码是：", sms_code)
