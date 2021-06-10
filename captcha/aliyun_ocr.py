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

    def __init__(self, appcode):
        from utils.logger import Log
        self.logger = Log().logger

        self.api_url = "https://ocrapi-advanced.taobao.com/ocrservice/advanced"
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
            self.logger.warning(resp)
        else:
            ocr_ret = json.loads(resp.text)["content"].strip(" ")
            self.logger.info("阿里云OCR识别结果：", ocr_ret)
            return ocr_ret

    def aliyun_ocr(self, _range, delay_time=5):
        """
        阿里云OCR识别数字
        :param _range: 验证码截图区域坐标(左x,左y,右x,右y)
        :param delay_time: ocr识别延迟时间
        :return: 识别到的数字
        """
        global sms_code
        BaiduOCR.get_code_pic(_range)
        img = open('ios_code_pic.png', 'rb').read()
        ocr_ret = self.post_url(img)

        if ocr_ret != "":
            find_all = re.findall(r'\'[\d]{6}\'', ocr_ret)
            if len(find_all) != 1:
                find_all = re.findall(r'([\d]{6})[\u3002]', ocr_ret)
            if len(find_all) != 1:
                find_all = re.findall(r'(您的验证码为[\d]{6})', ocr_ret)
            if len(find_all) != 1 and len(ocr_ret) == 6:
                find_all = re.findall(r'[\d]{6}', ocr_ret)

            if len(find_all) == 1:
                code = find_all[0].strip("'")
                if sms_code == code:
                    self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
                    time.sleep(delay_time)
                    return self.aliyun_ocr(_range, delay_time)
                else:
                    sms_code = code

                return code
            else:
                self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
                time.sleep(delay_time)
                return self.aliyun_ocr(_range, delay_time)
        else:
            self.logger.info("暂未获取到最新验证码，%d秒后重试" % delay_time)
            time.sleep(delay_time)
            return self.aliyun_ocr(_range, delay_time)


if __name__ == '__main__':
    from baidu_ocr import BaiduOCR

    _range = (1735, 357, 1816, 380)
    sms_code = AliYunOCR("").aliyun_ocr(_range, 4)
    print("阿里云OCR识别到的验证码是：", sms_code)
else:
    from captcha.baidu_ocr import BaiduOCR
