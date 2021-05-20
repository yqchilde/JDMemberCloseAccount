from PIL import ImageGrab
from aip import AipOcr


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
        self.get_code_pic(_range)
        img = open('ios_code_pic.png', 'rb').read()
        ret = self.client.basicGeneral(img)
        print(ret)
        if "words_result" in ret:
            return ret["words_result"][0]["words"]
        else:
            return ""
