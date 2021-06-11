import sys
import time
import json
import asyncio
import requests
import urllib3

from PIL import Image
from websockets import connect
from captcha.chaojiying import ChaoJiYing
from captcha.tujian import TuJian
from captcha.jd_captcha import JDcaptcha_base64
from utils.logger import Log
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
            recv = await asyncio.wait_for(websocket.recv(), get_config()["sms_captcha"]["ws_timeout"])
            return recv
        except asyncio.TimeoutError:
            return ""


logger = Log().logger


def INFO(*args):
    logger.info(" ".join(map(str, args)))


def WARN(*args):
    logger.warning(" ".join(map(str, args)))


def ERROR(*args):
    logger.error(" ".join(map(str, args)))


class JDMemberCloseAccount(object):
    """
    京东退店铺会员
    1. 全自动(超级鹰验证)
    2. 半自动(手动点击图形验证码)
    """

    def __init__(self):
        # 初始化基础配置
        self.config = get_config()
        self.selenium_cfg = get_config()["selenium"]
        self.shop_cfg = get_config()["shop"]
        self.sms_captcha_cfg = get_config()["sms_captcha"]
        self.image_captcha_cfg = get_config()["image_captcha"]
        self.ocr_cfg = self.sms_captcha_cfg["ocr"]

        # 初始化selenium配置
        self.browser = get_browser(self.selenium_cfg)
        self.wait = WebDriverWait(self.browser, self.selenium_cfg["selenium_timeout"])

        # 初始化短信验证码配置
        if self.sms_captcha_cfg["is_ocr"]:
            if self.ocr_cfg["type"] == "":
                WARN("当前已开启OCR模式，但是并未选择OCR类型，请在config.yaml补充ocr.type")
                sys.exit(1)
            if self.ocr_cfg["type"] == "baidu":
                from captcha.baidu_ocr import BaiduOCR
                self.baidu_ocr = BaiduOCR(
                    self.ocr_cfg["baidu_app_id"],
                    self.ocr_cfg["baidu_api_key"],
                    self.ocr_cfg["baidu_secret_key"]
                )
            elif self.ocr_cfg["type"] == "aliyun":
                from captcha.aliyun_ocr import AliYunOCR
                self.aliyun_ocr = AliYunOCR(
                    self.ocr_cfg["aliyun_appcode"]
                )
            elif self.ocr_cfg["type"] == "easyocr":
                from captcha.easy_ocr import EasyOCR
                self.easy_ocr = EasyOCR()

        # 初始化图形验证码配置
        if self.image_captcha_cfg["type"] == "cjy":
            self.cjy = ChaoJiYing(
                self.image_captcha_cfg["cjy_username"],
                self.image_captcha_cfg["cjy_password"],
                self.image_captcha_cfg["cjy_soft_id"]
            )
        elif self.image_captcha_cfg["type"] == "tj":
            self.tj = TuJian(
                self.image_captcha_cfg["tj_username"],
                self.image_captcha_cfg["tj_password"]
            )

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
            'cookie': self.config["cookie"],
            'charset': 'UTF-8',
            'accept-encoding': 'br,gzip,deflate',
            'user-agent': 'okhttp/3.12.1;jdmall;android;version/9.5.2;build/87971;screen/1080x2266;os/11;network/wifi;',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'content-length': '60'
        }

        card_list = []
        urllib3.disable_warnings()
        resp = requests.request("POST", url, headers=headers, data=payload, verify=False)
        ret = json.loads(resp.text)
        if ret["code"] == "0":
            if ret["message"] == "用户未登录":
                WARN("config.json 中的 mobile_cookie 值有误，请确保pt_key和pt_pin都存在，如都存在请检查是否失效")
                sys.exit(1)

            if "cardList" not in ret["result"]:
                INFO("当前卡包中会员店铺为0个")
                sys.exit(0)

            card_list = (ret["result"]["cardList"])
        else:
            ERROR(ret)

        return card_list

    def refresh_cache(self):
        """
        利用待领卡接口刷新卡包列表缓存
        :return:
        """
        url = "https://api.m.jd.com/client.action?functionId=getWalletUnreceivedCardList_New&clientVersion=10.0.2" \
              "&build=88569&client=android&d_brand=Xiaomi&d_model=M2007J3SC&osVersion=11&screen=2266*1080&partner" \
              "=xiaomi001&oaid=e02a70327f315862&openudid=3dab9a16bd95e38a&eid=eidA24e181233bsdmxzC3hIpQF2nJhWGGLb" \
              "%2F1JscxFOzBjvkqrXbFQyAXZmstKs0K6bUwkQ0D3s1%2F7MzLZ7JDdhztfcdZur9xPTxU1ahqtHWYb54%2FyNK&sdkVersion=30" \
              "&lang=zh_CN&uuid=3dab9a16bd95e38a&aid=3dab9a16bd95e38a&area=13_1000_40488_54442&networkType=wifi" \
              "&wifiBssid=unknown&uts=0f31TVRjBSsa33%2BKCXYEGxOEcvF5WoCTLW6zy4ICUIZSJDN7StKCM709NzfQ4TH7UyK43CcV9m" \
              "8NBxDef2fv9lr5dGonowgeJ4YODX5Jeb5TRw1PUE0YmmEdsQw4TlvNc5umf1j%2FKrR%2F3FAfMh%2Bs8nQ%2BG8trnDhaJW2kJKg" \
              "Hzq7N3es4kOmO4MEmUYf2putd%2BK0ZMPqJ8MfHJCta74kmAA%3D%3D&uemps=0-0&st=1623387008796&sign=d8297b1521c" \
              "0d56cdf290e2de658452e&sv=100"
        payload = "body=%7B%22pageNum%22%3A1%2C%22pageSize%22%3A10%2C%22v%22%3A%224.3%22%2C%22version%22%3A1580659200" \
                  "%7D&"
        headers = {
            'Host': 'api.m.jd.com',
            'cookie': self.config["cookie"],
            'charset': 'UTF-8',
            'accept-encoding': 'br,gzip,deflate',
            'user-agent': 'okhttp/3.12.1;jdmall;android;version/9.5.2;build/88569;screen/1080x2266;os/11;network/wifi;',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'content-length': '102'
        }
        urllib3.disable_warnings()
        resp = requests.request("POST", url, headers=headers, data=payload, verify=False)
        ret = json.loads(resp.text)
        if ret["code"] == "0":
            return True
        else:
            ERROR(ret)
            return False

    def main(self):
        # 打开京东
        self.browser.get("https://m.jd.com/")

        # 写入 cookie
        self.browser.delete_all_cookies()
        for cookie in self.config['cookie'].split(";", 1):
            self.browser.add_cookie(
                {"name": cookie.split("=")[0], "value": cookie.split("=")[1].strip(";"), "domain": ".jd.com"}
            )
        self.browser.refresh()

        cache_card_list, cookie_valid, retried = [], True, 0
        cnt, member_close_max_number = 0, self.shop_cfg["member_close_max_number"]

        while True:
            # 获取店铺列表
            card_list = self.get_shop_cards()
            if len(card_list) == 0:
                INFO("当前没有加入的店铺信息")
                sys.exit(0)

            # 记录一下所有请求数据，防止第一轮做完之后缓存没有刷新导致获取的链接请求失败
            if len(cache_card_list) == 0:
                cache_card_list = [item['brandId'] for item in card_list]
            else:
                if retried >= 10:
                    INFO("连续%d次获取到相同的店铺列表，判断为%d分钟左右的缓存仍未刷新，即将退出程序" % (retried, retried / 2))
                    sys.exit(0)

                # 每次比较新一轮的数量对比上一轮，即新的列表集合是否是旧的子集
                new_card_list = [item['brandId'] for item in card_list]
                if set(new_card_list) <= set(cache_card_list) and len(new_card_list) == len(cache_card_list):
                    INFO("当前接口获取到的店铺列表和上一轮一致，认为接口缓存还未刷新，即将尝试刷新缓存")
                    if self.refresh_cache():
                        INFO("理论上缓存已经刷新成功，如页面未成功自动刷新请及时反馈")
                        continue
                    else:
                        INFO("当前接口获取到的店铺列表和上一轮一致，认为接口缓存还未刷新，30秒后会再次尝试")
                        time.sleep(30)
                        retried += 1
                        continue
                else:
                    cache_card_list = new_card_list

            # 加载需要跳过的店铺
            shops = []
            if self.shop_cfg['skip_shops'] != "":
                shops = self.shop_cfg['skip_shops'].split(",")

            INFO("本次运行获取到", len(card_list), "家店铺会员信息")
            for card in card_list:
                # 判断本次运行数是否达到设置
                if member_close_max_number != 0 and cnt >= member_close_max_number:
                    INFO("已注销店铺数达到配置中允许注销的最大次数，程序退出")
                    sys.exit(0)

                # 判断该店铺是否要跳过
                if card["brandName"] in shops:
                    INFO("发现需要跳过的店铺", card["brandName"])
                    continue

                try:
                    # 打开注销页面
                    self.browser.get(
                        "https://shopmember.m.jd.com/member/memberCloseAccount?venderId=" + card["brandId"]
                    )
                    INFO("开始注销店铺", card["brandName"])

                    # 检查当前店铺退会链接是否失效
                    # noinspection PyBroadException
                    try:
                        WebDriverWait(self.browser, 1).until(EC.presence_of_element_located(
                            (By.XPATH, "//p[text()='网络请求失败']")
                        ))
                        INFO("当前店铺退会链接已失效，即将跳过，当前店铺链接为：")
                        INFO("https://shopmember.m.jd.com/member/memberCloseAccount?venderId=" + card["brandId"])
                        cookie_valid = False
                        continue
                    except Exception as _:
                        cookie_valid = True
                        pass

                    # 检查手机尾号是否正确
                    if self.shop_cfg['phone_tail_number'] != "":
                        if self.wait.until(EC.presence_of_element_located(
                                (By.XPATH, "//div[@class='cm-ec']")
                        )).text[-4:] != self.shop_cfg['phone_tail_number']:
                            INFO("当前店铺手机尾号不是规定的尾号，已跳过")
                            continue

                    # 发送短信验证码
                    self.wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//button[text()='发送验证码']")
                    ), "发送短信验证码超时 " + card["brandName"]).click()

                    # 要连接的websocket地址
                    sms_code, ws_conn_url = "", self.sms_captcha_cfg["ws_conn_url"]

                    # ocr识别投屏验证码
                    if self.sms_captcha_cfg["is_ocr"]:
                        if len(self.ocr_cfg["ocr_range"]) != 4:
                            WARN("请在config.yaml中配置 ocr_range")
                            sys.exit(1)
                        else:
                            _range = (self.ocr_cfg["ocr_range"])
                            ocr_delay_time = self.ocr_cfg["ocr_delay_time"]
                            INFO("刚发短信，%d秒后识别验证码" % ocr_delay_time)
                            time.sleep(ocr_delay_time)

                            if self.ocr_cfg["type"] == "baidu":
                                sms_code = self.baidu_ocr.baidu_ocr(_range, ocr_delay_time)
                            elif self.ocr_cfg["type"] == "aliyun":
                                sms_code = self.aliyun_ocr.aliyun_ocr(_range, ocr_delay_time)
                            elif self.ocr_cfg["type"] == "easyocr":
                                sms_code = self.easy_ocr.easy_ocr(_range, ocr_delay_time)
                    else:
                        try:
                            recv = asyncio.get_event_loop().run_until_complete(ws_conn(ws_conn_url))
                            if recv == "":
                                INFO("等待websocket推送短信验证码超时，即将跳过", card["brandName"])
                                continue
                            else:
                                sms_code = json.loads(recv)["sms_code"]
                        except Exception as e:
                            WARN("请先启动 jd_wstool 工具监听退会短信验证码\n", e.args)
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

                    # 利用打码平台识别图形验证码并模拟点击
                    def auto_identify_captcha_click():
                        # 分割图形验证码
                        code_img = self.get_code_pic()
                        img = open('code_pic.png', 'rb').read()

                        pic_str, pic_id = "", ""
                        if self.image_captcha_cfg["type"] == "cjy":
                            # 调用超级鹰API接口识别点触验证码
                            INFO("开始调用超级鹰识别验证码")
                            resp = self.cjy.post_pic(img, self.image_captcha_cfg["cjy_kind"])
                            if "pic_str" in resp and resp["pic_str"] == "":
                                INFO("超级鹰验证失败，原因为：", resp["err_str"])
                            else:
                                pic_str = resp["pic_str"]
                                pic_id = resp["pic_id"]
                        elif self.image_captcha_cfg["type"] == "tj":
                            # 调用图鉴API接口识别点触验证码
                            INFO("开始调用图鉴识别验证码")
                            resp = self.tj.post_pic(img, self.image_captcha_cfg["tj_type_id"])
                            pic_str = resp["result"]
                            pic_id = resp["id"]

                        # 处理要点击的坐标
                        all_list = []
                        xy_list = []
                        x = int(pic_str.split(',')[0])
                        xy_list.append(x)
                        y = int(pic_str.split(',')[1])
                        xy_list.append(y)
                        all_list.append(xy_list)

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
                            INFO("验证码坐标识别出错，将上报平台处理")

                            # 上报错误的图片到平台
                            if self.image_captcha_cfg["type"] == "cjy":
                                self.cjy.report_error(pic_id)
                            elif self.image_captcha_cfg["type"] == "tj":
                                self.tj.report_error(pic_id)
                            return False
                        except Exception as _:
                            return True

                    # 本地识别图形验证码并模拟点击
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
                            INFO("正在通过本地引擎识别")
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
                                INFO("识别未果")
                                self.wait.until(
                                    EC.presence_of_element_located((By.XPATH, '//*[@class="jcap_refresh"]'))).click()
                        return False

                    # 识别点击，如果有一次失败将再次尝试一次，再失败就跳过
                    if self.image_captcha_cfg["type"] == "local":
                        if not local_auto_identify_captcha_click():
                            INFO("验证码位置点击错误，尝试再试一次")
                            local_auto_identify_captcha_click()
                    else:
                        if not auto_identify_captcha_click():
                            INFO("验证码位置点击错误，尝试再试一次")
                            auto_identify_captcha_click()

                    # 解绑成功页面
                    self.wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//div[text()='解绑会员成功']")
                    ), "图形验证码识别超时 " + card["brandName"])

                    time.sleep(1)
                    cnt += 1
                    INFO("本次运行已成功注销店铺会员数量为：", cnt)
                except Exception as e:
                    ERROR("发生了一点小问题：", e.args)

                    if self.config["debug"]:
                        import traceback
                        traceback.print_exc()

            if not cookie_valid:
                INFO("本轮全部店铺都失效，有可能是cookie失效导致，请重新添加手机端cookie")
                sys.exit(0)
            else:
                INFO("本轮店铺已执行完，即将开始获取下一轮店铺")


if __name__ == '__main__':
    JDMemberCloseAccount().main()
