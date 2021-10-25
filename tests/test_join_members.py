import json
import os
import sys
import time
import requests
import urllib3
from selenium.webdriver.common.by import By

from selenium.common import exceptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class JDMemberJoinAccount(object):
    """
    本测试文件仅用于加入店铺会员
    """

    def __init__(self, _config_, _browser_):
        # 初始化selenium配置
        self.config = _config_
        self.browser = _browser_
        self.wait = WebDriverWait(_browser_, _config_["selenium"]["timeout"])

    def get_wallet_unreceived_card_list(self):
        """
        获取未加入的店铺列表
        :return: 返回店铺列表
        """

        url = "https://api.m.jd.com/client.action?functionId=getWalletUnreceivedCardList_New&clientVersion=10.2.0&bu" \
              "ild=90900&client=android&partner=xiaomi001&oaid=e02a70327f315862&eid=eidA24e181233bsdmxzC3hIpQF2nJhWG" \
              "GLb/1JscxFOzBjvkqrXbFQyAXZmstKs0K6bUwkQ0D3s1/7MzLZ7JDdhztfcdZur9xPTxU1ahqtHWYb54/yNK&sdkVersion=30&la" \
              "ng=zh_CN&harmonyOs=0&networkType=wifi&uts=0f31TVRjBSt%2Bbgdu7jx7XmiJYNLbjakrcJ%2BAsjm3FOGKlrOLTnqezpa" \
              "%2B2oInpgHTrv59RvwcqLo%2FVY9CV0axGqAC7d9a%2F9HWgBFMBTxFwEoSsqYFt3flByCNOmWgDB01Q%2FCPgUjEScIJLTChgwRL" \
              "8gzJ%2BhBvWXi57kt8XiPiWvch5bz5tAZVQkJSqtpGI67WWUVgPody7POtuirwt7Gq0g%3D%3D&uemps=0-0&ext=%7B%22prstat" \
              "e%22%3A%220%22%7D&ef=1&ep=%7B%22hdid%22%3A%22JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw%3D%22%2C%22t" \
              "s%22%3A1635154372693%2C%22ridx%22%3A-1%2C%22cipher%22%3A%7B%22area%22%3A%22CJDpCJKmCP80CNG4EP81DNG0Cq" \
              "%3D%3D%22%2C%22d_model%22%3A%22JJSmCNdAC1DN%22%2C%22wifiBssid%22%3A%22DWCnD2DsY2Y1CQZtDzG0DWC2DtPuDWZ" \
              "wEJqzYwU3CNY%3D%22%2C%22osVersion%22%3A%22CJO%3D%22%2C%22d_brand%22%3A%22WQvrb21f%22%2C%22screen%22%3" \
              "A%22CtS2DsenCNqm%22%2C%22uuid%22%3A%22C2HrYtvrCJZsZNu1ZJC4YG%3D%3D%22%2C%22aid%22%3A%22C2HrYtvrCJZsZN" \
              "u1ZJC4YG%3D%3D%22%2C%22openudid%22%3A%22C2HrYtvrCJZsZNu1ZJC4YG%3D%3D%22%7D%2C%22ciphertype%22%3A5%2C%" \
              "22version%22%3A%221.2.0%22%2C%22appname%22%3A%22com.jingdong.app.mall%22%7D&"

        page_num = 20
        var_name = locals()
        var_name["sign_page1"] = "st=1635154436173&sign=1f4be3f9be4f5effe544d0731062d765&sv=120"
        var_name["sign_page2"] = "st=1635154447514&sign=93907805bdaf031c986be25ba1ae7a07&sv=100"
        var_name["sign_page3"] = "st=1635154448415&sign=04e0fea07f03c5647907df1f31b61c2c&sv=120"
        var_name["sign_page4"] = "st=1635154449151&sign=f04d7f19de171edc43d1eae9e0579aed&sv=110"
        var_name["sign_page5"] = "st=1635154449932&sign=d81467bc4b3ec0baa4777a19ae411584&sv=111"
        var_name["sign_page6"] = "st=1635154450813&sign=13395d9b32dcd586ad9ce39b889fdbf2&sv=110"
        var_name["sign_page7"] = "st=1635154452316&sign=8aed00ddabf695067e902df69986e2ba&sv=112"
        var_name["sign_page8"] = "st=1635154453354&sign=e3b76fd8957360e79169fa3353f8bb16&sv=110"
        var_name["sign_page9"] = "st=1635154455072&sign=100ceb499cc425b8104b4a6bc34525d1&sv=102"
        var_name["sign_page10"] = "st=1635154456182&sign=01ec2eb343fa2371b8186ba9635b32bc&sv=112"
        var_name["sign_page11"] = "st=1635154456983&sign=7863b9fc73a82af6decf59adfebc73b0&sv=101"
        var_name["sign_page12"] = "st=1635154457841&sign=4c7fe932601be218989cc16efe6e2af7&sv=122"
        var_name["sign_page13"] = "st=1635154458798&sign=4f21e0bf982776e2ace458e1162d8725&sv=120"
        var_name["sign_page14"] = "st=1635154460127&sign=4a3676569c014989b264e97c9d7eaea3&sv=102"
        var_name["sign_page15"] = "st=1635154463410&sign=07562c7821497f50113504d337fd7485&sv=122"
        var_name["sign_page16"] = "st=1635154464574&sign=d2f142ce74446ec0ecbc4854452237d8&sv=120"
        var_name["sign_page17"] = "st=1635154466224&sign=8849b8be57ab33ed85ec9f7b981d09cd&sv=101"
        var_name["sign_page18"] = "st=1635154467186&sign=bdca274d26d536937d001e1bebc5d9e9&sv=101"
        var_name["sign_page19"] = "st=1635154469175&sign=dffde98c04176f76bcbe7edf46985af4&sv=111"
        var_name["sign_page20"] = "st=1635154470414&sign=28c8de16fddb70174134b5f6268c4432&sv=111"

        headers = {
            'Host': 'api.m.jd.com',
            'cookie': self.config["cookie"],
            'charset': 'UTF-8',
            'accept-encoding': 'br,gzip,deflate',
            'user-agent': self.config["user-agent"][1],
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'content-length': '60'
        }

        card_list = []
        urllib3.disable_warnings()

        for i in range(1, page_num + 1):
            body = "body=%7B%22pageNum%22%3A{}%2C%22pageSize%22%3A10%2C%22v%22%3A%225.0%22%2C%22" \
                   "version%22%3A1580659200%7D&".format(str(i))
            resp = requests.request(
                "POST",
                url + var_name.get("sign_page" + str(i)), headers=headers, data=body,
                verify=False
            )
            if resp.content:
                ret = json.loads(resp.text)
                if ret["code"] == "0":
                    if ret["message"] == "用户未登录":
                        print("config.yaml中的cookie值有误，请确保pt_key和pt_pin都存在，如都存在请检查cookie是否失效")
                        sys.exit(1)
                    elif ret["message"] == "响应成功":
                        if len(ret["result"]["cardList"]) == 0:
                            break
                        card_list.extend(ret["result"]["cardList"])
                else:
                    print(ret)
                    break
            else:
                print("获取卡包列表接口返回None，请检查网络")
                break
        return card_list

    def main(self):
        # 打开京东
        self.browser.get("https://m.jd.com/")

        # 检查Cookie配置
        if self.config["cookie"] == "":
            print("请先在 config.yaml 里配置好cookie")
            sys.exit(1)

        # 写入Cookie
        self.browser.delete_all_cookies()
        for cookie in self.config['cookie'].split(";", 1):
            self.browser.add_cookie(
                {"name": cookie.split("=")[0].strip(" "), "value": cookie.split("=")[1].strip(";"), "domain": ".jd.com"}
            )
        self.browser.refresh()

        while True:
            # 获取店铺列表
            card_list = self.get_wallet_unreceived_card_list()
            if len(card_list) == 0:
                print("没有获取到未加入店铺数据")
                sys.exit(0)

            print("本轮运行获取到", len(card_list), "家未加入店铺会员信息")
            for card in card_list:
                try:
                    # 打开店铺页面
                    print("开始进入店铺", card["brandName"])
                    self.browser.get(
                        "https://shopmember.m.jd.com/shopcard/?venderId=" + card["brandId"]
                    )

                    # 判断是否已经在页面
                    print("===判断是否已经在页面")
                    try:
                        if WebDriverWait(self.browser, 1).until(EC.presence_of_element_located(
                                (By.XPATH, "//span[text()='我的积分']")
                        )).text:
                            print("已是店铺会员")
                            continue
                    except exceptions.TimeoutException:
                        pass

                    # 勾选协议
                    print("===勾选协议")
                    self.wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//div[@class='react-view']/following-sibling::span[1]/preceding-sibling::div[1]")
                    ), "勾选协议失败 " + card["brandName"]).click()

                    # 点击加入店铺会员按钮
                    print("===点击加入店铺会员按钮")
                    self.wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//span[text()='确认授权并加入店铺会员']")
                    ), "加入店铺会员按钮点击失败 " + card["brandName"]).click()

                    time.sleep(1)
                except Exception as e:
                    print("发生了一点小问题：", e.args)

                    if self.config["debug"]:
                        import traceback
                        traceback.print_exc()
                    sys.exit(1)

            print("本轮店铺已执行完，即将开始获取下一轮店铺")


if __name__ == '__main__':
    from utils.config import get_config
    from utils.selenium_browser import get_browser

    _config_ = get_config("../config.yaml")
    _browser_ = get_browser(_config_, "../")

    obj = JDMemberJoinAccount(_config_, _browser_)
    obj.main()
