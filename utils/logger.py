import os
import time
import logging
from logging import handlers


# 单例
def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]

    return inner


@singleton
class Log(object):
    """
    输出日志类
    """

    def __init__(self):
        self.logger = logging.getLogger("")

        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.mkdir(logs_dir)

        # 设置日志文件名和日志格式
        log_file = time.strftime("%Y%m%d", time.localtime()) + ".log"
        log_path = os.path.join(logs_dir, log_file)

        # 追加写入日志
        rotating_file_handler = handlers.RotatingFileHandler(
            filename=log_path,
            encoding="utf-8"
        )
        self.format_str = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s', '%Y-%m-%d %H:%M:%S')
        rotating_file_handler.setFormatter(self.format_str)

        # 终端输出
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(self.format_str)

        # 绑定 handler
        self.logger.addHandler(rotating_file_handler)
        self.logger.addHandler(console)
        self.logger.setLevel(logging.INFO)

    def logger(self):
        return self.logger


if __name__ == "__main__":
    logger = Log().logger
    logger.info("Test info")
    logger.error("Test error")
