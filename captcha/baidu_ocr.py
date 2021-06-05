import re
import time
import easyocr

from PIL import ImageGrab
from aip import AipOcr
from utils.config import get_config

sms_code = ""


class BaiduOCR(object):
    """
    百度ocr识别类，用于帮助ios设备识别投屏后的短信验证码
    """

    def __init__(self, app_id, app_key, secret_key):
        self.config = get_config()
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
        self.get_code_pic(_range)
        img = open('ios_code_pic.png', 'rb').read()
        ret = self.client.basicGeneral(img)
        # 加这个是为了很多人不知道OCR为啥识别不到，如果介意请注释
        print(ret)
        if "words_result" in ret or self.config["easy_ocr"]:
            if self.config["easy_ocr"]:
                reader = easyocr.Reader(['ch_sim','en'])
                result = reader.readtext('ios_code_pic.png')
                find_all = re.findall(r"'[\d]{6}'", str(result))
                print(f"easy-ocr:{len(find_all)}\n"
                      f"{str(result)}")
                if len(find_all) == 1:
                    code = find_all[0]
                    if sms_code == code:
                        print("暂未获取到最新验证码，%d秒后重试" % delay_time)
                        time.sleep(delay_time)
                        return self.baidu_ocr(_range, delay_time)
                    else:
                        sms_code = code

                    return code
                else:
                    print("暂未获取到最新验证码，%d秒后重试" % delay_time)
                    time.sleep(delay_time)
                    return self.baidu_ocr(_range, delay_time)
            else:
                if len(ret["words_result"]) == 0:
                    print("暂未获取到最新验证码，%d秒后重试" % delay_time)
                    time.sleep(delay_time)
                    return self.baidu_ocr(_range, delay_time)

                code, length = "", len(ret["words_result"])

                for idx, words in enumerate(ret["words_result"]):
                    find_all = re.findall(r'[\d]{6}', words["words"])
                    if len(find_all) == 1:
                        code = find_all[0]
                        if sms_code == code:
                            print("暂未获取到最新验证码，%d秒后重试" % delay_time)
                            time.sleep(delay_time)
                            return self.baidu_ocr(_range, delay_time)
                        else:
                            sms_code = code

                        return code
                    else:
                        find_all = re.findall(r'([\d]{6})[\u3002]', words["words"])
                        if len(find_all) == 0:
                            if idx == length - 1:
                                print("暂未获取到最新验证码，%d秒后重试" % delay_time)
                                time.sleep(delay_time)
                                return self.baidu_ocr(_range, delay_time)
                            else:
                                continue
                        elif len(find_all) >= 1:
                            print(find_all)
                            code = find_all[0]
                            if sms_code == code:
                                print("暂未获取到最新验证码，%d秒后重试" % delay_time)
                                time.sleep(delay_time)
                                return self.baidu_ocr(_range, delay_time)
                            else:
                                sms_code = code

                        return code
        else:
            print("暂未获取到最新验证码，%d秒后重试" % delay_time)
            time.sleep(delay_time)
            return self.baidu_ocr(_range, delay_time)


if __name__ == '__main__':
    _range = (2634, 514, 3686, 1468)
    sms_code = BaiduOCR("", "", "").baidu_ocr(_range, 10)
    print("百度OCR识别到的验证码是：", sms_code)
