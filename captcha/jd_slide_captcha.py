import cv2
import base64
import random
import numpy as np
from PIL import Image


class JDSlideCaptcha(object):
    """
    京东滑块验证码识别
    """

    def base64_conversion(self, data):
        """
        base64转Mat
        :param data:
        :return:
        """
        imgData = base64.b64decode(data)
        nparr = np.frombuffer(imgData, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    def detect(self, cpc_img_path_base64, pcp_show_picture_path_base64):
        bg = self.base64_conversion(cpc_img_path_base64)
        slide = self.base64_conversion(pcp_show_picture_path_base64)

        # 灰度处理
        bg = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)
        slide = cv2.cvtColor(slide, cv2.COLOR_BGR2GRAY)

        # 清理滑块四周
        slide = slide[slide.any(1)]

        # 相似匹配
        result = cv2.matchTemplate(bg, slide, method=cv2.TM_CCOEFF_NORMED)

        # 提取匹配到的图像左上角坐标
        x, y = np.unravel_index(np.argmax(result), result.shape)

        # 使用openCV进行画框
        # ret = cv2.rectangle(bg, (y, x), (y + slide.shape[1], x + slide.shape[0]), (0, 0, 255), 2)
        # cv2.imwrite('result.jpg', ret)

        # 返回滑块距离
        # w, h = Image.open(bg).size

        return y / bg.shape[1]
