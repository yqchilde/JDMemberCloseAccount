import os
import sys

from utils.config import get_file
from selenium import webdriver
from selenium.common.exceptions import WebDriverException


def get_browser(_config):
    """
    获取浏览器对象
    :return:
    """
    browser_type = _config['browserType']
    headless = _config['headless']
    binary = _config['binary']
    user_agent = "Mozilla/5.0 (Linux; Android 9; COR-AL00) AppleWebKit/537.36 (KHTML, like Gecko) " \
                 "Chrome/77.0.3865.116 Mobile Safari/537.36 EdgA/46.03.4.5155 "
    try:
        if browser_type == 'Chrome':
            chrome_options = webdriver.ChromeOptions()
            # 防止在某些情况下报错`
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
            chrome_options.add_argument(f'user-agent={user_agent}')
            if binary != "":
                # 当找不到浏览器时需要在 config 里配置路径
                chrome_options.binary_location = binary
            if headless:
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--disable-gpu')
            if sys.platform == 'linux':
                _browser = webdriver.Chrome(executable_path=get_file("./drivers/chromedriver"), desired_capabilities={},
                                            options=chrome_options)
            elif sys.platform == 'darwin':
                _browser = webdriver.Chrome(executable_path=get_file("./drivers/chromedriver"), desired_capabilities={},
                                            options=chrome_options)
            elif sys.platform == 'win32':
                _browser = webdriver.Chrome(executable_path=get_file("./drivers/chromedriver"), desired_capabilities={},
                                            options=chrome_options)
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
                _browser = Edge(executable_path=get_file("./drivers/msedgedriver"), options=edge_options,
                                capabilities={})
            elif sys.platform == 'darwin':
                _browser = Edge(executable_path=get_file("./drivers/msedgedriver"), capabilities={},
                                options=edge_options)
            elif sys.platform == 'win32':
                _browser = Edge(executable_path=get_file("./drivers/msedgedriver"), capabilities={},
                                options=edge_options)
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
                _browser = webdriver.Firefox(executable_path=get_file('./drivers/geckodriver'), options=firefox_options,
                                             service_log_path=get_file("./logs/geckodriver.log"))
            elif sys.platform == 'darwin':
                _browser = webdriver.Firefox(executable_path=get_file('./drivers/geckodriver'), options=firefox_options)
            elif sys.platform == 'win32':
                _browser = webdriver.Firefox(executable_path=get_file('./drivers/geckodriver'), options=firefox_options)
        else:
            raise WebDriverException
        return _browser
    except WebDriverException:
        # 驱动问题
        print("ERROR", "浏览器错误", "请检查你的驱动和配置")
