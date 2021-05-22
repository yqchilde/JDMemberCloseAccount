import re
import time

from PIL import ImageGrab
from aip import AipOcr

from windowsjb import fetch_image

sms_code = ""


class BaiduOCR(object):
    """
    百度ocr识别类，用于帮助ios设备识别投屏后的短信验证码
    """

    def __init__(self, app_id, app_key, secret_key):
        self.client = AipOcr(app_id, app_key, secret_key)

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
        # self.get_code_pic(_range)
        fetch_image()
        img = open('ios_code_pic.png', 'rb').read()
        ret = self.client.basicGeneral(img)
        # 加这个是为了很多人不知道OCR为啥识别不到，如果介意请注释
        print(ret)
        if "words_result" in ret:
            if len(ret["words_result"]) == 0:
                print("暂未获取到最新验证码，%d秒后重试" % delay_time)
                time.sleep(delay_time)
                return self.baidu_ocr(_range, delay_time)

            code = ""
            # find_all = re.findall(r'[\d]{6}', ret["words_result"][0]["words"])
            # if len(find_all) == 0:
            #     print("暂未获取到最新验证码，%d秒后重试" % delay_time)
            #     time.sleep(delay_time)
            #     return self.baidu_ocr(_range, delay_time)
            # elif len(find_all) >= 1:
            #     code = find_all[0]
            #     if sms_code == code:
            #         print("暂未获取到最新验证码，%d秒后重试" % delay_time)
            #         time.sleep(delay_time)
            #         return self.baidu_ocr(_range, delay_time)
            #     else:
            #         sms_code = code
            for song in ret['words_result']:
                if ('您的验证码为' in song['words']):
                    code = song['words']
                    break
            code = re.findall(r"\d+\.?\d*", code)[0]
            code = int(code)
            if sms_code == "":
                sms_code = code
            # elif sms_code == code:
            #     print("暂未获取到最新验证码，5秒后重试")
            #     time.sleep(5)
            #     return self.baidu_ocr(_range)
            return code
        else:
            print("暂未获取到最新验证码，%d秒后重试" % delay_time)
            time.sleep(delay_time)
            return self.baidu_ocr(_range, delay_time)
