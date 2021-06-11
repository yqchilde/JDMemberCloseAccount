import os
import sys
import re
import time

from PIL import ImageGrab
from aip import AipOcr

sms_code = ""
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class BaiduOCR(object):
    """
    百度ocr识别类，用于帮助ios设备识别投屏后的短信验证码
    """

    def __init__(self, _config):
        from utils.logger import Log
        self.logger = Log().logger

        app_id = _config["baidu_app_id"]
        api_key = _config["baidu_api_key"]
        secret_key = _config["baidu_secret_key"]
        if app_id == "" or api_key == "" or secret_key == "":
            self.logger.warning("请在config.yaml中配置baidu ocr相关配置")
            sys.exit(1)
        self.client = AipOcr(app_id, api_key, secret_key)

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

    def baidu_ocr(self, _range, delay_time=5):
        """
        百度ocr识别数字
        :param delay_time: ocr识别延迟时间
        :param _range: 验证码截图区域坐标(左x,左y,右x,右y)
        :return: 识别到的数字
        """
        global sms_code
        self.get_code_pic(_range)
        img = open('ios_code_pic.png', 'rb').read()
        ret = self.client.basicGeneral(img)
        # 加这个是为了很多人不知道OCR为啥识别不到，如果介意请注释
        self.logger.info(ret)
        if "words_result" in ret:
            if len(ret["words_result"]) == 0:
                self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
                time.sleep(delay_time)
                return self.baidu_ocr(_range, delay_time)

            ocr_ret = str(ret["words_result"])
            find_all = re.findall(r'\'[\d]{6}\'', ocr_ret)
            if len(find_all) != 1:
                find_all = re.findall(r'([\d]{6})[\u3002]', ocr_ret)
            if len(find_all) != 1:
                find_all = re.findall(r'(您的验证码为[\d]{6})', ocr_ret)

            if len(find_all) == 1:
                code = find_all[0].strip("'")
                if sms_code == code:
                    self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
                    time.sleep(delay_time)
                    return self.baidu_ocr(_range, delay_time)
                else:
                    sms_code = code

                return code
            else:
                self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
                time.sleep(delay_time)
                return self.baidu_ocr(_range, delay_time)
        else:
            self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
            time.sleep(delay_time)
            return self.baidu_ocr(_range, delay_time)


if __name__ == '__main__':
    from utils.config import get_config

    ocr_cfg = get_config("../config.yaml")["sms_captcha"]["ocr"]
    _range = ocr_cfg["ocr_range"]
    sms_code = BaiduOCR(ocr_cfg).baidu_ocr(_range, ocr_cfg["ocr_delay_time"])
    print("百度OCR识别到的验证码是：", sms_code)
