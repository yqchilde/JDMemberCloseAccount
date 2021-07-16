#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021-06-21 11:33
# @Author  : 178
import cv2
import base64
import numpy as np
import os
import sys

class JDyolocaptcha(object):
    """
    yolov4类
    """
    def __init__(self, _config):
        self.CONFIDENCE_THRESHOLD = 0.8  # 置信阈值
        self.NMS_THRESHOLD = 0.01  # 非极大值抑制
        from utils.logger import Log
        self.logger = Log().logger
        weights = _config['yolov4_weights']
        cfg = _config['yolov4_cfg']
        if os.path.exists(weights):
            self.net = cv2.dnn.readNet(weights, cfg)
        else:
            self.logger.warning(f"找不到权重文件，当前工作目录{os.getcwd()} 应为{os.path.dirname(os.path.dirname(__file__))} 正在尝试更换工作目录")
            os.chdir(os.path.dirname(os.path.dirname(__file__)))
            if os.path.exists(weights):
                self.logger.info('已找到权重文件')
                self.net = cv2.dnn.readNet(weights, cfg)
            else:
                self.logger.error(f"找不到权重文件，请检查权重文件路径是否正确{os.getcwd()}/{weights}，及时进行反馈")
                sys.exit(1)
        self.model = cv2.dnn_DetectionModel(self.net)
        size = (_config['yolov4_net_size'], _config['yolov4_net_size'])
        self.model.setInputParams(size=size, scale=1/255, swapRB=True)


    def base64_conversion(self, data):
        """
        base64转Mat
        :param data:
        :return:
        """
        imgData = base64.b64decode(data.replace("data:image/jpg;base64,", ""))
        nparr = np.frombuffer(imgData, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


    def img_merge(self, cpc, pcp):
        """
        将两张图合成为一张大图，节省一次识别次数
        :param cpc:
        :param pcp:
        :return:
        """
        img = np.zeros((206, 275, 3), np.uint8)
        img[0:170, 0:275] = cpc
        img[170:206, 167:275] = pcp
        return img


    def detect(self, cpc, pcp):
        """
        识别验证码并返回坐标
        :param cpc:
        :param pcp:
        :return:
        """
        try:
            classes, scores, boxes = self.model.detect(self.img_merge(cpc, pcp), self.CONFIDENCE_THRESHOLD, self.NMS_THRESHOLD)  # 将验证码进行识别
            classes, scores, boxes = classes.tolist(), scores.tolist(), boxes.tolist()  # 将识别结果转化为list
            pcp_index = boxes.index(max(boxes))  # 获得pcp的索引
            pcp_class = classes[pcp_index]  # 获得pcp类名
            classes.pop(pcp_index)  # 从识别结果中剔除pcp
            scores.pop(pcp_index)  # 从识别结果中剔除pcp
            boxes.pop(pcp_index)  # 从识别结果中剔除pcp
            x1, y1, x2, y2 = boxes[classes.index(pcp_class)]  # 从剩下的结果中找到坐标，如果不存在则报错返回False
            if x2 - x1 < 200:  # 防止识别到的结果是背景，早期训练的很差的时候有这种现象，现在应该不存在，大概可以删了吧
                r = (x1*2+x2)//2, (y1*2+y2)//2
                return True, r
            else:
                return False, (None, None)
        except:
            return False, (None, None)


    def JDyolo(self, cpc_img_path_base64, pcp_show_picture_path_base64):
        return self.detect(self.base64_conversion(cpc_img_path_base64), self.base64_conversion(pcp_show_picture_path_base64))
