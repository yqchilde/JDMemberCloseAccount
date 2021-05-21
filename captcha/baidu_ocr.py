import time
import traceback

from PIL import ImageGrab
from aip import AipOcr

sms_code = ""


class BaiduOCR(object):
    """
    百度ocr识别类，用于帮助ios设备识别投屏后的短信验证码
    """

    def __init__(self, app_id, app_key, secret_key):
        self.ocr_api = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"
        self.token_api = "https://aip.baidubce.com/oauth/2.0/token"
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

    def baidu_ocr(self, _range):
        """
        百度ocr识别数字
        :param _range:
        :return:
        """
        global sms_code
        self.get_code_pic(_range)
        img = open('ios_code_pic.png', 'rb').read()
        ret = self.client.basicGeneral(img)
        if "words_result" in ret:
            if len(ret["words_result"]) == 0:
                print("未识别到验证码，5秒后重试")
                time.sleep(5)
                return self.baidu_ocr(_range)

            try:
                code = int(ret["words_result"][0]["words"])
                if sms_code == code:
                    print("暂未获取到最新验证码，5秒后重试")
                    time.sleep(5)
                    return self.baidu_ocr(_range)
                else:
                    sms_code = code

                return code
            except IndexError:
                print("未识别到验证码，5秒后重试")
                time.sleep(5)
                return self.baidu_ocr(_range)
            except ValueError as _:
                print("未识别到验证码，5秒后重试")
                time.sleep(5)
                return self.baidu_ocr(_range)

        else:
            print("未识别到验证码，5秒后重试")
            time.sleep(5)
            return self.baidu_ocr(_range)
