import os
import re
import sys
import time
import easyocr

sms_code = ""
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class EasyOCR(object):
    """
    EasyOCR识别类，用于帮助ios设备识别投屏后的短信验证码
    """

    def __init__(self, debug=False):
        from utils.logger import Log
        self.logger = Log().logger
        self.debug = debug

    def easy_ocr(self, _range_, delay_time=5):
        """
        easy ocr识别数字
        :param delay_time: ocr识别延迟时间
        :param _range_: 验证码截图区域坐标(左x,左y,右x,右y)
        :return: 识别到的数字
        """
        global sms_code
        screenshot_save(_range_)
        reader = easyocr.Reader(['ch_sim', 'en'])
        ocr_ret = str(reader.readtext(captcha_screenshot))

        # debug模式打印识别内容
        if self.debug:
            self.logger.info(str(ocr_ret))

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
                return self.easy_ocr(_range_, delay_time)
            else:
                sms_code = code

            return code
        else:
            self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
            time.sleep(delay_time)
            return self.easy_ocr(_range_, delay_time)


if __name__ == '__main__':
    from utils.config import get_config

    ocr_cfg = get_config("../config.yaml")["sms_captcha"]["ocr"]
    _range_ = ocr_cfg["ocr_range"]
    sms_code = EasyOCR(True).easy_ocr(_range_, ocr_cfg["ocr_delay_time"])
    print("Easy OCR识别到的验证码是：", sms_code)
else:
    from captcha.config import *
