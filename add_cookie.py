import json

from utils.config import get_config, get_file
from utils.selenium_browser import get_browser
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

if __name__ == '__main__':
    """
    用于获取web端cookie
    """
    config = get_config()
    config['headless'] = False
    browser = get_browser(config)
    browser.get("https://passport.jd.com/new/login.aspx")
    try:
        wait = WebDriverWait(browser, 35)
        username = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'nickname'))).text
        user = {
            "userName": username,
            "cookie": browser.get_cookies()
        }
        config['users'] = user
        with open(get_file("./config.json"), mode='w', encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print("成功添加", username)
    except WebDriverException:
        print("添加失败")
    finally:
        browser.close()
