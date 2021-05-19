import os
import sys
import json


def get_file(file_name=""):
    """
    获取文件绝对路径, 防止在某些情况下报错
    :param file_name: 文件名
    :return:
    """
    return os.path.join(os.path.split(sys.argv[0])[0], file_name)


def get_config():
    """
    获取配置
    :return:
    """
    return json.load(open(get_file("config.json"), 'r', encoding='utf-8'))
