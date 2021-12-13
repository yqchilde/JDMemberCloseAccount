import os
import sys
import re
import time

from aip import AipOcr

sms_code = ""
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class BaiduOCR(object):
    """
    百度ocr识别类，用于帮助ios设备识别投屏后的短信验证码
    """

    def __init__(self, _config, debug=False):
        from utils.logger import Log
        self.logger = Log().logger
        app_id = _config["baidu_app_id"]
        api_key = _config["baidu_api_key"]
        secret_key = _config["baidu_secret_key"]
        self.debug = debug
        if app_id == "" or api_key == "" or secret_key == "":
            self.logger.warning("请在config.yaml中配置baidu ocr相关配置")
            sys.exit(1)
        self.client = AipOcr(app_id, api_key, secret_key)

    def baidu_ocr(self, _range_, delay_time=5):
        """
        百度ocr识别数字
        :param delay_time: ocr识别延迟时间
        :param _range_: 验证码截图区域坐标(左x,左y,右x,右y)
        :return: 识别到的数字
        """

        global sms_code
        screenshot_save(_range_)
        img = open(captcha_screenshot, 'rb').read()
        ocr_ret = self.client.basicGeneral(img)

        # debug模式打印识别内容
        if self.debug:
            self.logger.info(ocr_ret)

        if "words_result" in ocr_ret:
            if len(ocr_ret["words_result"]) == 0:
                self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
                time.sleep(delay_time)
                return self.baidu_ocr(_range_, delay_time)

            ocr_ret = str(ocr_ret["words_result"])

            find_all = ""
            for rule in matching_rules:
                find_all = re.findall(rule, ocr_ret)
                if len(find_all) >= 1:
                    break

            if len(find_all) >= 1:
                code = find_all[0].strip("'")
                if sms_code == code:
                    self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
                    time.sleep(delay_time)
                    return self.baidu_ocr(_range_, delay_time)
                else:
                    sms_code = code

                return code
            else:
                self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
                time.sleep(delay_time)
                return self.baidu_ocr(_range_, delay_time)
        else:
            self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
            time.sleep(delay_time)
            return self.baidu_ocr(_range_, delay_time)


if __name__ == '__main__':
    from utils.config import get_config

    ocr_cfg = get_config("../config.yaml")["sms_captcha"]["ocr"]
    _range_ = ocr_cfg["ocr_range"]
    sms_code = BaiduOCR(ocr_cfg, True).baidu_ocr(_range_, ocr_cfg["ocr_delay_time"])
    print("百度OCR识别到的验证码是：", sms_code)
else:
    from captcha.config import *
