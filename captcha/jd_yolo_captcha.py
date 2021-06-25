#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021-06-21 11:33
# @Author  : 178
import cv2
import base64
import numpy as np

CONFIDENCE_THRESHOLD = 0.8  # 最低置信度
NMS_THRESHOLD = 0.01  # 去除重复匹配

# 导入网络
net = cv2.dnn.readNet("./yolov4/yolov4-custom.weights", "./yolov4/yolov4-custom.cfg")  # 标准权重

# 尝试使用cuda加速，需要编译安装opencv，具体可自信查找教程，据说速度可提升几倍到几十倍
# net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
# net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

# 由于两张图片大小不一样，因此要使用两个不同大小的网络去识别，否则识别率极低
cpc_model = cv2.dnn_DetectionModel(net)
pcp_model = cv2.dnn_DetectionModel(net)
cpc_model.setInputParams(size=(320, 320), scale=1/255, swapRB=True)  # size为32的倍数
pcp_model.setInputParams(size=(160, 160), scale=1/255, swapRB=True)  # size为32的倍数


def base64_conversion(data):
    """
    base64转Mat
    :param data:
    :return:
    """
    imgData = base64.b64decode(data.replace("data:image/jpg;base64,", ""))
    nparr = np.frombuffer(imgData, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


def identify(cpc, pcp):
    """
    识别验证码并返回坐标
    :param cpc:
    :param pcp:
    :return:
    """
    try:
        cpc_classes, cpc_scores, cpc_boxes = cpc_model.detect(cpc, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
        pcp_classes, pcp_scores, pcp_boxes = pcp_model.detect(pcp, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
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


def JDyolo(cpc_img_path_base64, pcp_show_picture_path_base64):
    return identify(base64_conversion(cpc_img_path_base64), base64_conversion(pcp_show_picture_path_base64))
