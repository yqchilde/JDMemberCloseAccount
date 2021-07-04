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
        self.CONFIDENCE_THRESHOLD = 0.8  # 最低置信度
        self.NMS_THRESHOLD = 0.01  # 去除重复匹配
        from utils.logger import Log
        self.logger = Log().logger
        weights = _config['yolov4_weights']
        cfg = _config['yolov4_cfg']
        if os.path.exists(weights):
            self.net = cv2.dnn.readNet(weights, cfg)
        else:
            self.logger.error("找不到权重文件")
            sys.exit(1)
        if _config['CUDA']:
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        # 由于两张图片大小不一样，因此要使用两个不同大小的网络去识别，否则识别率极低
        self.cpc_model = cv2.dnn_DetectionModel(self.net)
        self.pcp_model = cv2.dnn_DetectionModel(self.net)
        self.cpc_model.setInputParams(size=(320, 320), scale=1/255, swapRB=True)  # size为32的倍数，越大越慢，但不一定识别率越高
        self.pcp_model.setInputParams(size=(224, 128), scale=1/255, swapRB=True)  # size为32的倍数


    def base64_conversion(self, data):
        """
        base64转Mat
        :param data:
        :return:
        """
        imgData = base64.b64decode(data.replace("data:image/jpg;base64,", ""))
        nparr = np.frombuffer(imgData, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


    def identify(self, cpc, pcp):
        """
        识别验证码并返回坐标
        :param cpc:
        :param pcp:
        :return:
        """
        try:
            cpc_classes, cpc_scores, cpc_boxes = self.cpc_model.detect(cpc, self.CONFIDENCE_THRESHOLD, self.NMS_THRESHOLD)
            pcp_classes, pcp_scores, pcp_boxes = self.pcp_model.detect(pcp, self.CONFIDENCE_THRESHOLD, self.NMS_THRESHOLD)
            if pcp_classes[0] in cpc_classes:  # 判断识别小图的结果是否在大图里面
                x1, y1, x2, y2 = cpc_boxes[cpc_classes.tolist().index(pcp_classes[0])]
                if x2 - x1 < 200:  # 防止结果为背景，因此要剔除x差值在200以上的结果
                    r = (x1*2+x2)//2, (y1*2+y2)//2
                    return True, r
                else:
                    return False, (None, None)
            else:
                return False, (None, None)
        except:
            return False, (None, None)


    def JDyolo(self, cpc_img_path_base64, pcp_show_picture_path_base64):
        return self.identify(self.base64_conversion(cpc_img_path_base64), self.base64_conversion(pcp_show_picture_path_base64))