import re
import time

import easyocr

from captcha.baidu_ocr import BaiduOCR

sms_code = ""


class EasyOCR(object):
    """
    EasyOCR识别类，用于帮助ios设备识别投屏后的短信验证码
    """

    def __init__(self):
        pass

    def easy_ocr(self, _range, delay_time=5):
        """
        easy ocr识别数字
        :param delay_time: ocr识别延迟时间
        :param _range: 验证码截图区域坐标(左x,左y,右x,右y)
        :return: 识别到的数字
        """
        global sms_code
        BaiduOCR.get_code_pic(_range)

        reader = easyocr.Reader(['ch_sim', 'en'])
        result = reader.readtext('ios_code_pic.png')
        find_all = re.findall(r'\'[\d]{6}\'', str(result))
        print(f"easy-ocr:{len(find_all)}\n"
              f"{str(result)}")

        if len(find_all) == 1:
            code = find_all[0].strip("'")

            if sms_code == code:
                print("暂未获取到最新验证码，%d秒后重试" % delay_time)
                time.sleep(delay_time)
                return self.easy_ocr(_range, delay_time)
            else:
                sms_code = code

            return code
        else:
            print("暂未获取到最新验证码，%d秒后重试" % delay_time)
            time.sleep(delay_time)
            return self.easy_ocr(_range, delay_time)


if __name__ == '__main__':
    _range = (3460, 590, 3658, 638)
    sms_code = EasyOCR().easy_ocr(_range, 4)
    print("Easy OCR识别到的验证码是：", sms_code)
