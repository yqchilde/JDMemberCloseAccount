import os
import sys
import time

from utils.config import get_file
from selenium import webdriver
from selenium.common.exceptions import WebDriverException


def get_browser(_config_, path_prefix=""):
    """
    获取浏览器对象
    :return:
    """
    browser_type = _config_['selenium']['browserType']
    headless = _config_['selenium']['headless']
    binary = _config_['selenium']['binary']
    user_agent = _config_['user-agent'][0]
    _browser_ = None
    try:
        if browser_type == 'Chrome':
            chrome_options = webdriver.ChromeOptions()
            # 防止在某些情况下报错`
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument("--incognito")  # 无痕模式
            chrome_options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
            chrome_options.add_argument(f'user-agent={user_agent}')
            if binary != "":
                # 当找不到浏览器时需要在 config 里配置路径
                chrome_options.binary_location = binary
            if headless:
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--disable-gpu')
            if sys.platform == 'linux':
                _browser_ = webdriver.Chrome(
                    executable_path=get_file(path_prefix + "./drivers/chromedriver"),
                    desired_capabilities={},
                    options=chrome_options
                )
            elif sys.platform == 'darwin':
                _browser_ = webdriver.Chrome(
                    executable_path=get_file(path_prefix + "./drivers/chromedriver"),
                    desired_capabilities={},
                    options=chrome_options
                )
            elif sys.platform == 'win32':
                _browser_ = webdriver.Chrome(
                    executable_path=get_file(path_prefix + "./drivers/chromedriver"),
                    desired_capabilities={},
                    options=chrome_options
                )
            _browser_.set_window_size(500, 700)
        elif browser_type == 'Edge':
            from msedge.selenium_tools import Edge, EdgeOptions
            edge_options = EdgeOptions()
            edge_options.use_chromium = True
            edge_options.add_argument('--no-sandbox')
            edge_options.add_argument('--disable-dev-shm-usage')
            edge_options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
            if binary != "":
                edge_options.binary_location = binary
            if headless:
                edge_options.add_argument('--headless')
                edge_options.add_argument('--disable-gpu')
            if sys.platform == 'linux':
                _browser_ = Edge(
                    executable_path=get_file(path_prefix + "./drivers/msedgedriver"),
                    options=edge_options,
                    capabilities={}
                )
            elif sys.platform == 'darwin':
                _browser_ = Edge(
                    executable_path=get_file(path_prefix + "./drivers/msedgedriver"),
                    capabilities={},
                    options=edge_options
                )
            elif sys.platform == 'win32':
                _browser_ = Edge(
                    executable_path=get_file(path_prefix + "./drivers/msedgedriver"),
                    capabilities={},
                    options=edge_options
                )
            _browser_.set_window_size(500, 700)
        elif browser_type == 'Firefox':
            # 先清除上次的日志
            if not os.path.exists(get_file("./logs")):
                os.mkdir(get_file("./logs/"))
            open(get_file("./logs/geckodriver.log"), "w").close()

            firefox_options = webdriver.FirefoxOptions()
            firefox_options.log.level = "fatal"
            if binary != "":
                firefox_options.binary_location = binary
            if headless:
                firefox_options.add_argument('--headless')
                firefox_options.add_argument('--disable-gpu')
            if sys.platform == 'linux':
                _browser_ = webdriver.Firefox(
                    executable_path=get_file('./drivers/geckodriver'),
                    options=firefox_options,
                    service_log_path=get_file("./logs/geckodriver.log")
                )
            elif sys.platform == 'darwin':
                _browser_ = webdriver.Firefox(
                    executable_path=get_file('./drivers/geckodriver'),
                    options=firefox_options
                )
            elif sys.platform == 'win32':
                _browser_ = webdriver.Firefox(
                    executable_path=get_file('./drivers/geckodriver'),
                    options=firefox_options
                )
            _browser_.set_window_size(500, 700)
        else:
            raise WebDriverException
        return _browser_
    except WebDriverException as e:
        # 驱动问题
        if "This version of ChromeDriver only supports Chrome version" in e.args.__str__():
            print("\r[%s] [ERROR] 浏览器错误(chromedriver版本错误)，请比对前三位版本号" %
                  (
                      time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                  ))
        elif "'chromedriver' executable needs to be in PATH" in e.args.__str__():
            print("\r[%s] [ERROR] 浏览器错误，请检查你下载并解压好的驱动是否放在drivers目录下" %
                  (
                      time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                  ))
        elif "unknown error: cannot find Chrome binary" in e.args.__str__():
            print("\r[%s] [ERROR] 浏览器错误(Chrome浏览器可执行文件路径未成功识别)，请在配置文件中修改selenium.binary为浏览器可执行文件绝对路径" %
                  (
                      time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                  ))
        else:
            print("\r[%s] [ERROR] 浏览器错误， 请检查你下载并解压好的驱动是否放在drivers目录下，如需帮助请及时反馈; err: %s" %
                  (
                      time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                      e.args.__str__()
                  ))
        sys.exit(1)
