import sys
import time
import json
import asyncio
import requests

from PIL import Image
from websockets import connect
from captcha.chaojiying import ChaoJiYing
from captcha.tujian import TuJian
from captcha.jd_captcha import JDcaptcha_base64
from captcha.baidu_ocr import BaiduOCR
from utils.config import get_config
from utils.selenium_browser import get_browser
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


async def ws_conn(ws_conn_url):
    """
    websocket连接
    """
    async with connect(ws_conn_url) as websocket:
        try:
            recv = await asyncio.wait_for(websocket.recv(), get_config()["ws_timeout"])
            return recv
        except asyncio.TimeoutError:
            return ""


class JDMemberCloseAccount(object):
    """
    京东退店铺会员
    1. 全自动(超级鹰验证)
    2. 半自动(手动点击图形验证码)
    """

    def __init__(self):
        self.config = get_config()
        self.browser = get_browser(self.config)
        self.wait = WebDriverWait(self.browser, self.config["selenium_timeout"])
        self.cjy_kind = self.config["cjy_kind"]
        self.cjy = ChaoJiYing(self.config["cjy_username"], self.config["cjy_password"], self.config["cjy_soft_id"])
        self.tj = TuJian(self.config["tj_username"], self.config["tj_password"])
        self.baidu_ocr = BaiduOCR(self.config["baidu_app_id"], self.config["baidu_api_key"],
                                  self.config["baidu_secret_key"])

    def get_code_pic(self, name='code_pic.png'):
        """
        获取验证码图像
        :param name:
        :return:
        """

        # 确定验证码的左上角和右下角坐标
        code_img = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='captcha_modal']//div")))
        location = code_img.location
        size = code_img.size
        _range = (int(location['x']), int(location['y']), (int(location['x']) + int(size['width'])),
                  (int(location['y']) + int(size['height'])))

        # 将整个页面截图
        self.browser.save_screenshot(name)

        # 获取浏览器大小
        window_size = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='root']")))
        width, height = window_size.size['width'], window_size.size['height']

        # 图片根据窗口大小resize，避免高分辨率影响坐标
        i = Image.open(name)
        new_picture = i.resize((width, height))
        new_picture.save(name)

        # 剪裁图形验证码区域
        code_pic = new_picture.crop(_range)
        code_pic.save(name)
        time.sleep(2)
        return code_img

    def get_shop_cards(self):
        """
        获取加入店铺列表
        :return: 返回店铺列表
        """

        url = "https://api.m.jd.com/client.action?functionId=getWalletReceivedCardList_New&clientVersion=9.5.2&build" \
              "=87971&client=android&d_brand=Xiaomi&d_model=M2007J3SC&osVersion=11&screen=2266*1080&partner=xiaomi001" \
              "&oaid=e02a70327f315862&openudid=3dab9a16bd95e38a&eid=eidA24e181233bsdmxzC3hIpQF2nJhWGGLb" \
              "%2F1JscxFOzBjvkqrXbFQyAXZmstKs0K6bUwkQ0D3s1%2F7MzLZ7JDdhztfcdZur9xPTxU1ahqtHWYb54%2FyNK&sdkVersion=30" \
              "&lang=zh_CN&uuid=3dab9a16bd95e38a&aid=3dab9a16bd95e38a&area=13_1000_40488_54442&networkType=wifi" \
              "&wifiBssid=c609e931512437a8806ae06b86d3977b&uts=0f31TVRjBSsu47QjbY5aZUsO5LYa1B%2F3wqL7JjlFB60vmw6" \
              "%2F8Xbj74d3sWoT4CTQgX7X0M07W75JvIfz5eu7NxdNJ73NSVbgTHkdsiVZ770PEn0MWPywxr4glUdddS6uxIQ5VfPG65uoUmlB6" \
              "%2BBwwDqO1Nfxv8%2Bdm15xR%2BFG4fJWb6wCFO7DFMtnoOMo2CQ8mYoECYG3qT%2Bso7P%2FKLgQcg%3D%3D&uemps=0-0&st" \
              "=1620105615175&sign=65996ece830b41aabdaba32c9d782d07&sv=100"
        payload = "body=%7B%22v%22%3A%224.1%22%2C%22version%22%3A1580659200%7D&"
        headers = {
            'Host': 'api.m.jd.com',
            'cookie': self.config["mobile_cookie"],
            'charset': 'UTF-8',
            'accept-encoding': 'br,gzip,deflate',
            'user-agent': 'okhttp/3.12.1;jdmall;android;version/9.5.2;build/87971;screen/1080x2266;os/11;network/wifi;',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'content-length': '60'
        }

        card_list = []
        resp = requests.request("POST", url, headers=headers, data=payload)
        ret = json.loads(resp.text)
        if ret["code"] == "0":
            if ret["message"] == "用户未登录":
                print("config.json 中的 mobile_cookie 值有误，请确保pt_key和pt_pin都存在，如都存在请检查是否失效")
                sys.exit(1)

            if "cardList" not in ret["result"]:
                print("当前卡包中会员店铺为0个")
                sys.exit(1)

            card_list = (ret["result"]["cardList"])
        else:
            print("echo")

        return card_list

    def main(self):
        # 打码平台只能启用一个
        if self.config["cjy_validation"] and self.config["tj_validation"]:
            print("打码平台只能选择一个使用，不可两个都开启")
            sys.exit(1)

        # 打开京东
        self.browser.get("https://m.jd.com/")
        # msShortcutLogin
        # 写入 cookie
        self.browser.delete_all_cookies()
        for cookie in self.config['mobile_cookie'].split(";"):
            self.browser.add_cookie({"name": cookie.split("=")[0], "value": cookie.split("=")[1], "domain": ".jd.com"})
        self.browser.refresh()

        self.browser.set_window_size(500, 700)

        cache_brand_id, pc_cookie_valid, retried = "", True, 0
        cnt, member_close_max_number = 0, self.config["member_close_max_number"]

        while True:
            # 获取店铺列表
            card_list = self.get_shop_cards()
            if len(card_list) == 0:
                print("当前没有加入的店铺信息")
                sys.exit(0)

            # 记录一下所有请求数据，防止第一轮做完之后缓存没有刷新导致获取的链接请求失败
            if cache_brand_id == "":
                cache_brand_id = card_list
            else:
                if retried >= 5:
                    print("连续五次获取到相同的店铺列表，退出程序")
                    sys.exit(0)
                if cache_brand_id == card_list:
                    print("当前接口获取到的店铺列表和上一轮一致，认为接口缓存还未刷新，30秒后会再次尝试")
                    time.sleep(30)
                    retried += 1
                    continue

            # 加载需要跳过的店铺
            shops = []
            if self.config['skip_shops'] != "":
                shops = self.config['skip_shops'].split(",")

            print("本次运行获取到", len(card_list), "家店铺会员信息")
            for card in card_list:
                # 判断本次运行数是否达到设置
                if member_close_max_number != 0 and cnt >= member_close_max_number:
                    print("已注销店铺数达到配置中允许注销的最大次数，程序退出")
                    sys.exit(0)

                # 判断该店铺是否要跳过
                if card["brandName"] in shops:
                    print("发现需要跳过的店铺", card["brandName"])
                    continue

                try:
                    # 打开注销页面
                    self.browser.get(
                        "https://shopmember.m.jd.com/member/memberCloseAccount?venderId=" + card["brandId"])
                    print("开始注销店铺", card["brandName"])

                    # 检查当前店铺退会链接是否失效
                    # noinspection PyBroadException
                    try:
                        WebDriverWait(self.browser, 1).until(EC.presence_of_element_located(
                            (By.XPATH, "//p[text()='网络请求失败']")
                        ))
                        print("当前店铺退会链接已失效，即将跳过，当前店铺链接为：")
                        print("https://shopmember.m.jd.com/member/memberCloseAccount?venderId=" + card["brandId"])
                        pc_cookie_valid = False
                        continue
                    except Exception as _:
                        pc_cookie_valid = True
                        pass

                    # 检查手机尾号是否正确
                    if self.config['phone_tail_number'] != "":
                        if self.wait.until(EC.presence_of_element_located(
                                (By.XPATH, "//div[@class='cm-ec']")
                        )).text[-4:] != self.config['phone_tail_number']:
                            print("当前店铺手机尾号不是规定的尾号，已跳过")
                            continue

                    # 发送短信验证码
                    self.wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//button[text()='发送验证码']")
                    ), "发送短信验证码超时 " + card["brandName"]).click()

                    # 要连接的websocket地址
                    sms_code, ws_conn_url = "", self.config["ws_conn_url"]
                    # 如果是IOS设备，去ocr识别投屏验证码
                    if self.config["device"] == "ios":
                        if self.config["baidu_range"] == "":
                            print("请在config.json中配置需要截取的手机短信验证码区域坐标")
                            sys.exit(1)
                        else:
                            _range = (self.config["baidu_range"])
                            ocr_delay_time = self.config["baidu_delay_time"]
                            sms_code = self.baidu_ocr.baidu_ocr(_range, ocr_delay_time)
                    else:
                        try:
                            recv = asyncio.get_event_loop().run_until_complete(ws_conn(ws_conn_url))
                            if recv == "":
                                print("等待websocket推送短信验证码超时，即将跳过", card["brandName"])
                                continue
                            else:
                                sms_code = json.loads(recv)["sms_code"]
                        except Exception as e:
                            print("请先启动 jd_wstool 监听退会短信验证码\n", e.args)
                            sys.exit(1)

                    # 输入短信验证码
                    self.wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//input[@type='number']")
                    ), "输入短信验证码超时 " + card["brandName"]).send_keys(sms_code)
                    time.sleep(1)

                    # 点击注销按钮
                    self.wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//div[text()='注销会员']")
                    ), "点击注销按钮超时 " + card["brandName"]).click()

                    # 识别并点击封装一下
                    def auto_identify_captcha_click():
                        # 使用超级鹰验证 或 图鉴验证
                        t = True
                        if self.config["cjy_validation"] or self.config["tj_validation"] or t:
                            # 分割图形验证码
                            code_img = self.get_code_pic()
                            im = open('code_pic.png', 'rb').read()

                            # 调用超级鹰API接口识别点触验证码
                            pic_str, pic_id = "", ""
                            if self.config["cjy_validation"]:
                                print("开始调用超级鹰识别验证码")
                                resp = self.cjy.post_pic(im, self.cjy_kind)
                                if "pic_str" in resp and resp["pic_str"] == "":
                                    print("超级鹰验证失败，原因为：", resp["err_str"])
                                else:
                                    pic_str = resp["pic_str"]
                                    pic_id = resp["pic_id"]

                            # 调用图鉴API接口识别点触验证码
                            if self.config["tj_validation"]:
                                print("开始调用图鉴识别验证码")
                                resp = self.tj.post_pic(im, self.config["tj_type_id"])
                                if resp == "NoBalanceException: 余额不足":
                                    print("图鉴打码平台余额不足，请去充值！")
                                    sys.exit(0)
                                pic_str = resp["result"]
                                pic_id = resp["id"]

                            # 调用图鉴API接口识别点触验证码
                            all_list = []  # 存储被点击的坐标
                            xy_list = []
                            x = int(pic_str.split(',')[0])
                            xy_list.append(x)
                            y = int(pic_str.split(',')[1])
                            xy_list.append(y)
                            all_list.append(xy_list)
                            print(all_list)

                            # 循环遍历点击图片
                            for i in all_list:
                                x = i[0]
                                y = i[1]
                                ActionChains(self.browser).move_to_element_with_offset(code_img, x, y).click().perform()
                                time.sleep(1)

                            # 图形验证码坐标点击错误尝试重试
                            # noinspection PyBroadException
                            try:
                                WebDriverWait(self.browser, 3).until(EC.presence_of_element_located(
                                    (By.XPATH, "//p[text()='验证失败，请重新验证']")
                                ))
                                print("验证码坐标识别出错，将上报平台处理")

                                # 上报错误的图片到平台
                                if self.config["cjy_validation"]:
                                    self.cjy.report_error(pic_id)
                                if self.config["tj_validation"]:
                                    self.tj.report_error(pic_id)

                                return False
                            except Exception as _:
                                return True

                    def local_auto_identify_captcha_click():
                        for _ in range(4):
                            time.sleep(1)
                            cpc_img = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="cpc_img"]')))
                            zoom = cpc_img.size['height'] / 170
                            cpc_img_path_base64 = self.wait.until(
                                EC.presence_of_element_located((By.XPATH, '//*[@id="cpc_img"]'))).get_attribute(
                                'src').replace("data:image/jpeg;base64,", "")
                            pcp_show_picture_path_base64 = self.wait.until(EC.presence_of_element_located(
                                (By.XPATH, '//*[@class="pcp_showPicture"]'))).get_attribute('src')
                            # 正在识别验证码
                            print("正在通过本地引擎识别")
                            res = JDcaptcha_base64(cpc_img_path_base64, pcp_show_picture_path_base64)
                            if res[0]:
                                ActionChains(self.browser).move_to_element_with_offset(
                                    cpc_img, int(res[1][0] * zoom),
                                    int(res[1][1] * zoom)
                                ).click().perform()

                                # 图形验证码坐标点击错误尝试重试
                                # noinspection PyBroadException
                                try:
                                    WebDriverWait(self.browser, 3).until(EC.presence_of_element_located(
                                        (By.XPATH, "//p[text()='验证失败，请重新验证']")
                                    ))
                                    return False
                                except Exception as _:
                                    return True
                            else:
                                print("识别未果")
                                self.wait.until(
                                    EC.presence_of_element_located((By.XPATH, '//*[@class="jcap_refresh"]'))).click()
                        return False

                    # 识别点击，如果有一次失败将再次尝试一次，再失败就跳过
                    if self.config['cjy_validation'] or self.config['tj_validation']:
                        if not auto_identify_captcha_click():
                            print("验证码位置点击错误，尝试再试一次")
                            auto_identify_captcha_click()
                    else:
                        if not local_auto_identify_captcha_click():
                            print("验证码位置点击错误，尝试再试一次")
                            local_auto_identify_captcha_click()

                    # 解绑成功页面
                    self.wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//div[text()='解绑会员成功']")
                    ), "图形验证码识别超时 " + card["brandName"])

                    time.sleep(1)
                    cnt += 1
                    print("本次运行已成功注销店铺会员数量为：", cnt)
                except Exception as e:
                    print("发生了一点小问题：", e.args)

            if not pc_cookie_valid:
                print("本轮全部店铺都失效，有可能是电脑端cookie失效导致，请重新添加")
                sys.exit(1)
            else:
                print("本轮店铺已执行完，即将开始获取下一轮店铺")


if __name__ == '__main__':
    JDMemberCloseAccount().main()
