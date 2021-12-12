import os
import sys
import base64
import json
import re
import time
import requests

sms_code = ""
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class AliYunOCR(object):
    """
    阿里云OCR识别类，用于帮助ios设备识别投屏后的短信验证码
    """

    def __init__(self, _config, debug=False):
        from utils.logger import Log
        self.logger = Log().logger
        self.api_url = "https://ocrapi-advanced.taobao.com/ocrservice/advanced"
        self.debug = debug
        appcode = _config["aliyun_appcode"]
        if appcode == "":
            self.logger.warning("请在config.yaml中配置aliyun_appcode")
            sys.exit(1)
        self.appcode = appcode

    def post_url(self, img):
        headers = {
            "Authorization": "APPCODE %s" % self.appcode,
            "Content-Type": "application/json; charset=UTF-8"
        }

        img_base64 = base64.b64encode(img).decode()
        payload = {"img": img_base64}

        resp = requests.request("POST", url=self.api_url, headers=headers, data=json.dumps(payload))
        if resp.status_code != 200:
            self.logger.warning("阿里云OCR请求错误，错误原因：" + resp.text)
            self.logger.warning("阿里云OCR请求错误，大概率是次数用光，如非次数用光请将该问题反馈给开发者，程序即将退出")
            sys.exit(1)
        else:
            ocr_ret = json.loads(resp.text)["content"].strip(" ")
            return ocr_ret

    def aliyun_ocr(self, _range_, delay_time=5):
        """
        阿里云OCR识别数字
        :param _range_: 验证码截图区域坐标(左x,左y,右x,右y)
        :param delay_time: ocr识别延迟时间
        :return: 识别到的数字
        """
        global sms_code
        screenshot_save(_range_)
        img = open(captcha_screenshot, 'rb').read()
        ocr_ret = self.post_url(img)

        # debug模式打印识别内容
        if self.debug:
            self.logger.info(ocr_ret)

        if ocr_ret != "":
            find_all = ""
            for rule in matching_rules:
                find_all = re.findall(rule, ocr_ret)
                if len(find_all) >= 1:
                    break

            if len(find_all) == 1:
                code = find_all[0].strip("'")
                if sms_code == code:
                    self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
                    time.sleep(delay_time)
                    return self.aliyun_ocr(_range_, delay_time)
                else:
                    sms_code = code

                return code
            else:
                self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
                time.sleep(delay_time)
                return self.aliyun_ocr(_range_, delay_time)
        else:
            self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
            time.sleep(delay_time)
            return self.aliyun_ocr(_range_, delay_time)


if __name__ == '__main__':
    from utils.config import get_config
    from config import *

    ocr_cfg = get_config("../config.yaml")["sms_captcha"]["ocr"]
    _range_ = ocr_cfg["ocr_range"]
    sms_code = AliYunOCR(ocr_cfg, True).aliyun_ocr(_range_, ocr_cfg["ocr_delay_time"])
    print("阿里云OCR识别到的验证码是：", sms_code)
else:
    from captcha.config import *
