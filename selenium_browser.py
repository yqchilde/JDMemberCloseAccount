import sys

from utils import get_file
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

    try:
        if browser_type == 'Chrome':
            chrome_options = webdriver.ChromeOptions()
            # 防止在某些情况下报错`
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
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
        else:
            raise WebDriverException
        return _browser
    except WebDriverException:
        # 驱动问题
        print("ERROR", "浏览器错误", "请检查你的驱动和配置")
