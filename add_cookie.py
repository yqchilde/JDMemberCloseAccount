import re

from utils.config import get_config
from utils.selenium_browser import get_browser
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

if __name__ == '__main__':
    """
    用于获取手机端cookie
    """
    browser = get_browser(get_config())
    browser.get("https://plogin.m.jd.com/login/login")
    try:
        wait = WebDriverWait(browser, 135)
        print("请在网页端通过手机号码登录")
        wait.until(EC.presence_of_element_located((By.ID, 'msShortcutMenu')))
        browser.get("https://home.m.jd.com/myJd/newhome.action")
        username = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'my_header_name'))).text
        pt_key, pt_pin, cookie = "", "", ""
        for _ in browser.get_cookies():
            if _["name"] == "pt_key":
                pt_key = _["value"]
            if _["name"] == "pt_pin":
                pt_pin = _["value"]
            if pt_key and pt_pin:
                break
        cookie = "pt_key=" + pt_key + ";pt_pin=" + pt_pin + ";"
        print("获取的cookie是：" + cookie)

        new_lines = []
        rf = open("config.yaml", 'r', encoding='utf-8')
        line = rf.readline()
        while line:
            if "cookie:" in line:
                lineReg = re.compile(r'cookie: \"(.*?)\"')
                line = lineReg.sub('cookie: \"%s\"' % cookie, line)
            new_lines.append(line)
            line = rf.readline()
        rf.close()
        wf = open("config.yaml", 'w', encoding='utf-8')
        for line in new_lines:
            wf.write(line)
        wf.close()

        print("成功添加", username)
    except WebDriverException:
        print("添加失败")
    finally:
        browser.close()
