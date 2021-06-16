import os
import re
import sys
import time

from PIL import ImageGrab
from cnocr import CnOcr

sms_code = ""

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class CnOCR(object):
    """
    CnOCR识别类，用于帮助ios设备识别投屏后的短信验证码
    """

    def __init__(self):
        from utils.logger import Log
        self.logger = Log().logger

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

    def cn_ocr(self, _range, delay_time=5):
        """
        cn ocr识别数字
        :param delay_time: ocr识别延迟时间
        :param _range: 验证码截图区域坐标(左x,左y,右x,右y)
        :return: 识别到的数字
        """
        global sms_code
        self.get_code_pic(_range)

        cn_ocr = CnOcr(model_name="conv-lite-fc", context="cpu", root="conv-lite-fc")
        ret = cn_ocr.ocr("ios_code_pic.png")
        result = ""
        for v in ret:
            result += "".join(v)

        find_all = re.findall(r'\'[\d]{6}\'', str(result))
        if len(find_all) != 1:
            find_all = re.findall(r'([\d]{6})[\u3002]', str(result))
        if len(find_all) != 1:
            find_all = re.findall(r'(您的验证码为[\d]{6})', str(result))

        # 识别结果
        self.logger.info("CnOCR识别结果：" + result)

        if len(find_all) == 1:
            code = find_all[0].strip("'")

            if sms_code == code:
                self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
                time.sleep(delay_time)
                return self.cn_ocr(_range, delay_time)
            else:
                sms_code = code

            return code
        else:
            self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
            time.sleep(delay_time)
            return self.cn_ocr(_range, delay_time)


if __name__ == '__main__':
    from utils.config import get_config

    ocr_cfg = get_config("../config.yaml")["sms_captcha"]["ocr"]
    _range = ocr_cfg["ocr_range"]
    sms_code = CnOCR().cn_ocr(_range, ocr_cfg["ocr_delay_time"])
    print("CnOCR识别到的验证码是：", sms_code)
