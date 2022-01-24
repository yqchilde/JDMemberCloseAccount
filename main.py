import copy
import time
import json
import asyncio
import requests
import urllib3

from PIL import Image
import websockets.legacy.client
from captcha.chaojiying import ChaoJiYing
from captcha.tujian import TuJian
from captcha.jd_captcha import JDcaptcha_base64
from captcha.jd_yolo_captcha import JDyolocaptcha
from utils.logger import Log
from utils.config import get_config
from utils.validator import verify_configuration
from utils.version import check_version
from utils.selenium_browser import get_browser
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

logger = Log().logger


class JDMemberCloseAccount(object):
    """
    京东全自动退店铺会员
    """

    def INFO(self, *args):
        s = ''
        for item in list(map(str, args)):
            s += item
        logger.info("".join(self.pinname + " >> " + s))

    def WARN(self, *args):
        s = ''
        for item in list(map(str, args)):
            s += item
        logger.warning("".join(self.pinname + " >> " + s))

    def ERROR(self, *args):
        s = ''
        for item in list(map(str, args)):
            s += item
        logger.error("".join(self.pinname + " >> " + s))

    def __init__(self):
        self.pinname = ''
        self.INFO("欢迎执行JD全自动退会程序，如有使用问题请加TG群https://t.me/jdMemberCloseAccount进行讨论")
        self.INFO("↓  " * 30)

        # 检查版本
        self.INFO("开始检查项目是否有更新")
        check_version(logger)

        # 检查配置
        self.INFO("开始检查项目配置完整性")
        verify_configuration(logger)

        # 初始化基础配置
        self.config = get_config()
        self.selenium_cfg = get_config()["selenium"]
        self.shop_cfg = get_config()["shop"]
        self.sms_captcha_cfg = get_config()["sms_captcha"]
        self.image_captcha_cfg = get_config()["image_captcha"]
        self.ocr_cfg = self.sms_captcha_cfg["ocr"]
        self.debug = self.config["debug"]

        # 初始化selenium配置
        self.browser = get_browser(self.config)
        self.wait = WebDriverWait(self.browser, self.selenium_cfg["timeout"])
        self.wait_check = WebDriverWait(self.browser, self.selenium_cfg["check_wait"])

        # 初始化短信验证码配置
        if not self.sms_captcha_cfg["is_ocr"]:
            if not self.sms_captcha_cfg["jd_wstool"]:
                from utils.listener import SmsSocket
                self.sms = SmsSocket(int(get_config()["main"]["smsport"]))
        elif self.sms_captcha_cfg["is_ocr"]:
            self.ocr_type = self.ocr_cfg["type"]
            if self.ocr_type == "":
                self.WARN("当前已开启OCR模式，但是并未选择OCR类型，请在config.yaml补充ocr.type")
                return
            if self.ocr_type == "baidu":
                from captcha.baidu_ocr import BaiduOCR
                self.baidu_ocr = BaiduOCR(self.ocr_cfg, self.debug)
            elif self.ocr_type == "aliyun":
                from captcha.aliyun_ocr import AliYunOCR
                self.aliyun_ocr = AliYunOCR(self.ocr_cfg, self.debug)
            elif self.ocr_type == "easyocr":
                from captcha.easy_ocr import EasyOCR
                self.easy_ocr = EasyOCR(self.debug)
            elif self.ocr_type == "baidu_fanyi":
                from captcha.baidu_fanyi import BaiduFanYi
                self.baidu_fanyi = BaiduFanYi(self.ocr_cfg, self.debug)
        self.ws_conn_url = self.sms_captcha_cfg["ws_conn_url"]
        self.ws_timeout = self.sms_captcha_cfg["ws_timeout"]

        # 初始化图形验证码配置
        if self.image_captcha_cfg["type"] == "cjy":
            self.cjy = ChaoJiYing(self.image_captcha_cfg)
        elif self.image_captcha_cfg["type"] == "tj":
            self.tj = TuJian(self.image_captcha_cfg)
        elif self.image_captcha_cfg["type"] == "local":
            pass
        elif self.image_captcha_cfg["type"] == "manual":
            pass
        elif self.image_captcha_cfg["type"] == "yolov4":
            self.JDyolo = JDyolocaptcha(self.image_captcha_cfg)
        else:
            self.WARN("请在config.yaml中补充image_captcha.type")
            return

        # 初始化店铺变量
        # 错误店铺页面数量
        self.wrong_store_page_count = 0
        # 黑名单店铺缓存
        self.black_list_shops = []
        # 会员关闭最大数量
        self.member_close_max_number = self.shop_cfg["member_close_max_number"]
        # 注销成功店铺数量
        self.member_close_count = 0
        # 需要跳过的店铺
        self.need_skip_shops = []
        # 指定注销的店铺
        self.specify_shops = []
        # 页面失效打不开的店铺
        self.failure_store = []
        # 云端数据执行状态
        self.add_remote_shop_data = self.shop_cfg["add_remote_shop_data"]

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
        _range_ = (int(location['x']), int(location['y']), (int(location['x']) + int(size['width'])),
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
        code_pic = new_picture.crop(_range_)
        code_pic.save(name)
        time.sleep(2)
        return code_img

    def get_shop_cards(self):
        """
        获取加入店铺列表
        :return: 返回店铺列表
        """

        url = "https://api.m.jd.com/client.action?functionId=getWalletReceivedCardList_New&clientVersion=10.2.0&bui" \
              "ld=90900&client=android&partner=xiaomi001&oaid=e02a70327f315862&eid=eidA24e181233bsdmxzC3hIpQF2nJhWG" \
              "GLb/1JscxFOzBjvkqrXbFQyAXZmstKs0K6bUwkQ0D3s1/7MzLZ7JDdhztfcdZur9xPTxU1ahqtHWYb54/yNK&sdkVersion=30&l" \
              "ang=zh_CN&harmonyOs=0&networkType=wifi&uts=0f31TVRjBSto8DL4K0ee85ZRt0rmw128U%2B6PiicSyj%2Bq9U2tA0gWy" \
              "YjW29QZLyq5ebqz%2BLY0DD03RA0Pz%2B8PPqt%2FzmMyvdLqzrHQ4H1TLZ3qP0jDbUcDGjUcS0cJFuP%2F4Wb8%2Bi8BajbDrNw" \
              "9yU5V6OumYiQALp8Jxh82E9QhngZT7ybL1zuXSzO%2BLvCgdg6BockZnd9hKMTFq4pY4oMMsg%3D%3D&uemps=0-0&ext=%7B%22" \
              "prstate%22%3A%220%22%7D&ef=1&ep=%7B%22hdid%22%3A%22JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw%3D%22" \
              "%2C%22ts%22%3A1634992423397%2C%22ridx%22%3A-1%2C%22cipher%22%3A%7B%22area%22%3A%22CJDpCJKmCP80CNG4EP" \
              "81DNG0Cq%3D%3D%22%2C%22d_model%22%3A%22JJSmCNdAC1DN%22%2C%22wifiBssid%22%3A%22YzYmEWU5CzO1CJS0CzdrEN" \
              "qmDwPvCNZsENZuCzu3D2S%3D%22%2C%22osVersion%22%3A%22CJO%3D%22%2C%22d_brand%22%3A%22WQvrb21f%22%2C%22s" \
              "creen%22%3A%22CtS2DsenCNqm%22%2C%22uuid%22%3A%22C2HrYtvrCJZsZNu1ZJC4YG%3D%3D%22%2C%22aid%22%3A%22C2H" \
              "rYtvrCJZsZNu1ZJC4YG%3D%3D%22%2C%22openudid%22%3A%22C2HrYtvrCJZsZNu1ZJC4YG%3D%3D%22%7D%2C%22ciphertyp" \
              "e%22%3A5%2C%22version%22%3A%221.2.0%22%2C%22appname%22%3A%22com.jingdong.app.mall%22%7D&"

        page_num = 8
        var_name = locals()
        var_name["sign_page1"] = "st=1634992661020&sign=83a87e33d52a73c3abf01217af277d7c&sv=101"
        var_name["sign_page2"] = "st=1634992678131&sign=4da2fffa2375fd0f6f261ac70fcaad00&sv=102"
        var_name["sign_page3"] = "st=1634992682728&sign=83815a83dedef47c5f908269aca3926c&sv=100"
        var_name["sign_page4"] = "st=1634992686855&sign=f781c2707f70c8ffc98b28e091a56542&sv=121"
        var_name["sign_page5"] = "st=1634992688025&sign=15680ac47fb873561fc9f38ff2411a5e&sv=122"
        var_name["sign_page6"] = "st=1635177469421&sign=f9180d4e3989a78d07bf2dd4a276508c&sv=102"
        var_name["sign_page7"] = "st=1635177470330&sign=de73d5da876afa061c61068d987c5f40&sv=100"
        var_name["sign_page8"] = "st=1635177471053&sign=3305e1cf5833274f46169b4b8a811f4e&sv=100"

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
                        self.WARN("config.yaml中的cookie值有误，请确保pt_key和pt_pin都存在，如都存在请检查cookie是否失效")
                        return
                    elif ret["message"] == "响应成功":
                        if len(ret["result"]["cardList"]) == 0:
                            break
                        card_list.extend(ret["result"]["cardList"])
                else:
                    self.ERROR(ret)
                    break
            else:
                self.ERROR("获取卡包列表接口返回None，请检查网络")
                break

        # 添加店铺名字
        url = "https://gitee.com/yqchilde/Scripts/raw/main/jd/shop_all.json"
        try:
            resp = requests.get(url, timeout=30)
            if "该内容无法显示" in resp.text:
                return card_list

            shop_list = resp.json()
            for card in card_list:
                for shop in shop_list:
                    if card["brandName"] == shop["brandName"]:
                        card["shopName"] = shop["shopName"]
                        break
            return card_list
        except TimeoutError:
            pass
        finally:
            return card_list

    def refresh_cache(self):
        """
        利用待领卡接口刷新卡包列表缓存
        :return:
        """
        url = "https://api.m.jd.com/client.action?functionId=getWalletUnreceivedCardList_New&clientVersion=10.2.0&bu" \
              "ild=90900&client=android&partner=xiaomi001&oaid=e02a70327f315862&eid=eidA24e181233bsdmxzC3hIpQF2nJhWG" \
              "GLb/1JscxFOzBjvkqrXbFQyAXZmstKs0K6bUwkQ0D3s1/7MzLZ7JDdhztfcdZur9xPTxU1ahqtHWYb54/yNK&sdkVersion=30&la" \
              "ng=zh_CN&harmonyOs=0&networkType=wifi&uts=0f31TVRjBSto8DL4K0ee85ZRt0rmw1282OyO9rnqi1tOb%2F8sm56Ob%2B2" \
              "cXRa7tHz7%2Brbnij%2FrCELTlgkV7kZeS2bYJHn1VmbuhkPZ%2FEdKSyksnAupmrbGMSyCNb4zYaLOIo4Ctbtqd6Z9k3de%2BrTH" \
              "Uc0aeSTgZ%2FZ47Z%2Fe5b%2F%2Bt24iEsGelW3oJAs9OMvTYGqyA5dS%2BPKX5oHybFC4iYH2FA%3D%3D&uemps=0-0&ext=%7B%" \
              "22prstate%22%3A%220%22%7D&ef=1&ep=%7B%22hdid%22%3A%22JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw%3D%2" \
              "2%2C%22ts%22%3A1635004927990%2C%22ridx%22%3A-1%2C%22cipher%22%3A%7B%22area%22%3A%22CJDpCJKmCP80CNG4EP" \
              "81DNG0Cq%3D%3D%22%2C%22d_model%22%3A%22JJSmCNdAC1DN%22%2C%22wifiBssid%22%3A%22YzYmEWU5CzO1CJS0CzdrENq" \
              "mDwPvCNZsENZuCzu3D2S%3D%22%2C%22osVersion%22%3A%22CJO%3D%22%2C%22d_brand%22%3A%22WQvrb21f%22%2C%22scr" \
              "een%22%3A%22CtS2DsenCNqm%22%2C%22uuid%22%3A%22C2HrYtvrCJZsZNu1ZJC4YG%3D%3D%22%2C%22aid%22%3A%22C2HrYt" \
              "vrCJZsZNu1ZJC4YG%3D%3D%22%2C%22openudid%22%3A%22C2HrYtvrCJZsZNu1ZJC4YG%3D%3D%22%7D%2C%22ciphertype%22" \
              "%3A5%2C%22version%22%3A%221.2.0%22%2C%22appname%22%3A%22com.jingdong.app.mall%22%7D&st=1635004961154&" \
              "sign=398298f4fbaf3e8218626e5c447c73f6&sv=100"
        body = "body=%7B%22pageNum%22%3A1%2C%22pageSize%22%3A10%2C%22v%22%3A%225.0%22%2C%22version%22%3A1580659200%7D&"
        headers = {
            'Host': 'api.m.jd.com',
            'cookie': self.config["cookie"],
            'charset': 'UTF-8',
            'accept-encoding': 'br,gzip,deflate',
            'user-agent': self.config["user-agent"][1],
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'content-length': '102'
        }
        urllib3.disable_warnings()
        resp = requests.request("POST", url, headers=headers, data=body, verify=False)
        ret = json.loads(resp.text)
        if ret["code"] == "0":
            return True
        else:
            self.ERROR(ret)
            return False

    async def ws_conn(ws_conn_url, ws_timeout):
        """
        websocket连接
        """
        async with websockets.legacy.client.connect(ws_conn_url, compression=None) as websocket:
            try:
                recv = await asyncio.wait_for(websocket.recv(), ws_timeout)
                return recv
            except asyncio.TimeoutError:
                return ""

    def close_member(self, card, flag=0):
        """
        进行具体店铺注销页面的注销操作
        card: 具体店铺数据对象
        flag: 乱码页面挂载状态
        """

        # 页面链接
        page_link = "https://shopmember.m.jd.com/member/memberCloseAccount?venderId=" + card["brandId"]

        # 检查手机尾号是否正确
        phone = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[text()='手机号']/following-sibling::div[1]")
            )
        ).text

        if "*" not in phone[:4]:
            if flag == 0:
                if "AARm5gnNkBWoE8tQA5n" in phone:
                    self.INFO("当前店铺绑定手机号为%s，明显为无效号码，挂载到新标签页" % phone)
                    self.browser.execute_script('window.open("{}")'.format(page_link))
                    self.browser.switch_to.window(self.browser.current_window_handle)
                    self.wrong_store_page_count += 1
                else:
                    self.INFO("当前店铺绑定手机号为%s，明显为无效号码，程序加入黑名单后自动跳过" % phone)
            else:
                self.INFO("当前店铺绑定手机号为%s，明显为无效号码，程序加入黑名单后自动跳过" % phone)

            # 加入黑名单缓存
            if card not in self.black_list_shops:
                self.record_black_list(card)
            return False
        elif self.shop_cfg['phone_tail_number'] and phone[-4:] not in self.shop_cfg['phone_tail_number']:
            self.INFO("当前店铺绑定手机号为%s，尾号≠配置中设置的尾号，程序加入黑名单后自动跳过" % phone)
            # 加入黑名单缓存
            if card not in self.black_list_shops:
                self.record_black_list(card)
            return False

        # 发送短信验证码
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//button[text()='发送验证码']")
        ), "发送短信验证码超时 " + card["brandName"]).click()

        # 判断是否发送成功，发送失败为黑店，直接跳过
        self.wait_check.until(EC.presence_of_element_located(
            (By.XPATH, "//div[text()='发送成功']")
        ), f'发送失败，黑店【{card["brandName"]}】跳过')

        # 验证码
        sms_code = ""

        # ocr识别投屏验证码
        if self.sms_captcha_cfg["is_ocr"]:
            if len(self.ocr_cfg["ocr_range"]) != 4:
                self.WARN("请在config.yaml中配置 ocr_range")
                return
            else:
                _range_ = (self.ocr_cfg["ocr_range"])
                ocr_delay_time = self.ocr_cfg["ocr_delay_time"]
                self.INFO("刚发短信，%d秒后识别验证码" % ocr_delay_time)
                time.sleep(ocr_delay_time)

                if self.ocr_type == "baidu":
                    self.INFO("开始调用百度OCR识别")
                    sms_code = self.baidu_ocr.baidu_ocr(_range_, ocr_delay_time)
                elif self.ocr_type == "aliyun":
                    self.INFO("开始调用阿里云OCR识别")
                    sms_code = self.aliyun_ocr.aliyun_ocr(_range_, ocr_delay_time)
                elif self.ocr_type == "easyocr":
                    self.INFO("开始调用EasyOCR识别")
                    sms_code = self.easy_ocr.easy_ocr(_range_, ocr_delay_time)
                elif self.ocr_type == "baidu_fanyi":
                    self.INFO("开始调用百度翻译识别")
                    sms_code = self.baidu_fanyi.baidu_fanyi(_range_, ocr_delay_time)
                self.INFO("验证码识别结果为：", sms_code)
        else:
            try:
                if self.sms_captcha_cfg["jd_wstool"]:
                    recv = asyncio.get_event_loop().run_until_complete(self.ws_conn(self.ws_conn_url, self.ws_timeout))
                else:
                    recv = self.sms.get_code()

                if recv == "":
                    self.INFO("等待websocket推送短信验证码超时，即将跳过", card["brandName"])
                    self.record_black_list(card)
                    return False
                else:
                    sms_code = json.loads(recv)["sms_code"]
                self.INFO("验证码监听结果为：", sms_code)
            except OSError:
                self.WARN("WebSocket监听时发生了问题，请检查是否开启外部jd_wstool工具或者使用内置的jd_wstool或者5201端口是否开放")
                self.browser.close()
                return
            except Exception as e:
                self.WARN(e.__class__, e.args)
                return

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
                self.INFO("开始调用超级鹰识别验证码")
                resp = self.cjy.post_pic(img, self.image_captcha_cfg["cjy_kind"])
                if "pic_str" in resp and resp["pic_str"] == "":
                    self.INFO("超级鹰验证失败，原因为：", resp["err_str"])
                else:
                    pic_str = resp["pic_str"]
                    pic_id = resp["pic_id"]
            elif self.image_captcha_cfg["type"] == "tj":
                # 调用图鉴API接口识别点触验证码
                self.INFO("开始调用图鉴识别验证码")
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
                self.INFO("验证码坐标识别出错，将上报平台处理")

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
                cpc_img = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="cpc_img"]')))
                zoom = cpc_img.size['height'] / 170
                cpc_img_path_base64 = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="cpc_img"]'))).get_attribute(
                    'src').replace("data:image/jpeg;base64,", "")
                pcp_show_picture_path_base64 = self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@class="pcp_showPicture"]'))).get_attribute('src')
                # 正在识别验证码
                if self.image_captcha_cfg["type"] == "local":
                    self.INFO("正在通过本地引擎识别")
                    res = JDcaptcha_base64(cpc_img_path_base64, pcp_show_picture_path_base64)
                else:
                    self.INFO("正在通过深度学习引擎识别")
                    res = self.JDyolo.JDyolo(cpc_img_path_base64, pcp_show_picture_path_base64)
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
                        time.sleep(1)
                        return False
                    except Exception as _:
                        return True
                else:
                    self.INFO("识别未果")
                    self.wait.until(
                        EC.presence_of_element_located((By.XPATH, '//*[@class="jcap_refresh"]'))).click()
                    time.sleep(1)
                    return False
            return False

        # 识别点击，如果有一次失败将再次尝试一次，再失败就跳过
        if self.image_captcha_cfg["type"] in ["local", "yolov4"]:
            if not local_auto_identify_captcha_click():
                self.INFO("验证码位置点击错误，尝试再试一次")
                if not local_auto_identify_captcha_click():
                    self.INFO("验证码位置点击错误，跳过店铺")
                    return False
        elif self.image_captcha_cfg["type"] == "manual":
            self.INFO("请手动过验证码")
        else:
            if not auto_identify_captcha_click():
                self.INFO("验证码位置点击错误，尝试再试一次")
                if not auto_identify_captcha_click():
                    self.INFO("验证码位置点击错误，跳过店铺")
                    return False

        # 解绑成功页面
        try:
            self.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[text()='解绑会员成功']")
            ), f'解绑失败，黑店【{card["brandName"]}】跳过')
        except:
            sms_t = self.sms.get_code()
            print("可能是验证码时序没对上，丢弃一次验证码:" + sms_t)

        time.sleep(1)
        self.member_close_count += 1
        self.remove_black_list(card)
        if card["brandName"] in self.specify_shops:
            self.specify_shops.remove(card["brandName"])
        self.INFO("👌 本次运行已成功注销店铺会员数量为：", self.member_close_count)
        return True

    def record_black_list(self, card):
        """
        记录黑名单店铺
        :param card:
        :return:
        """
        if card not in self.black_list_shops:
            self.black_list_shops.append(card)
        if card["brandName"] not in self.need_skip_shops:
            self.need_skip_shops.append(card["brandName"])

    def remove_black_list(self, card):
        """
        移除黑名单店铺
        :param card:
        :return:
        """
        if card in self.black_list_shops:
            self.black_list_shops.remove(card)
        if card["brandName"] in self.need_skip_shops:
            self.need_skip_shops.remove(card["brandName"])

    def get_cloud_shop_ids(self):
        """
        获取云端店铺列表
        :return:
        """
        if not self.add_remote_shop_data:
            return True, []

        url = "https://gitee.com/yqchilde/Scripts/raw/main/jd/shop.json"
        try:
            resp = requests.get(url, timeout=60)
            if "该内容无法显示" in resp.text:
                return self.get_cloud_shop_ids()

            shop_list = resp.json()
            self.INFO("获取到云端商铺信息 %d 条" % len(shop_list))
            self.add_remote_shop_data = False
            return False, shop_list
        except Exception as e:
            self.ERROR("获取云端列表发生了一点小问题：", e.args)

    def main(self):
        # 打开京东
        self.browser.get("https://m.jd.com/")

        # 检查Cookie配置
        if self.config["cookie"] == "":
            self.WARN("请先在 config.yaml 里配置好cookie")
            self.browser.close()
            return

        ck = str(self.config["cookie"]).split(";")
        for item in ck:
            if "pin" in item:
                self.pinname = item.split("=")[1]
        if '%' in self.pinname:
            import urllib.parse
            self.pinname = urllib.parse.unquote(self.pinname)

        # 写入Cookie
        self.browser.delete_all_cookies()
        for cookie in self.config['cookie'].split(";", 1):
            self.browser.add_cookie(
                {"name": cookie.split("=")[0].strip(" "), "value": cookie.split("=")[1].strip(";"), "domain": ".jd.com"}
            )
        self.browser.refresh()

        # 设置黑名单店铺名字数组
        if len(self.shop_cfg["skip_shops"]) > 0:
            self.need_skip_shops = self.shop_cfg["skip_shops"]

        # 指定注销店铺配置优先级最高，且self.specify_shops需浅拷贝
        if len(self.shop_cfg["specify_shops"]) > 0:
            self.INFO("👀 发现已配置指定店铺，优先指定店铺，不执行需要跳过店铺")
            self.specify_shops = copy.copy(self.shop_cfg["specify_shops"])
            self.need_skip_shops = []

        # 检查列表接口缓存
        while True:
            # 执行一遍刷新接口
            self.refresh_cache()

            state, card_list = self.get_cloud_shop_ids()
            if state:
                # 获取店铺列表
                card_list = self.get_shop_cards()

            if len(card_list) == 0:
                self.INFO("🎉 本次运行获取到的店铺数为0个，判断为没有需要注销的店铺，即将退出程序")
                self.browser.close()
                return

            # 如果剩下的卡包
            if len(self.shop_cfg["specify_shops"]) > 0 and len(self.specify_shops) == 0:
                self.INFO("👋 指定店铺已全部注销完毕，程序即将退出")
                self.browser.close()
                return

            # 如果剩下的卡包全部都是黑名单中的，直接就结束
            # 每次比较新一轮的数量对比上一轮，即新的列表集合是否是旧的子集
            card_list_new = [item['brandId'] for item in card_list]
            card_list_black = [item['brandId'] for item in self.black_list_shops]
            if set(card_list_new) <= set(card_list_black):
                self.INFO("芜湖，剩下的店铺全部都在程序黑名单中")
                self.INFO("本次运行记录的黑名单店铺名字为", self.need_skip_shops)
                self.INFO("🤔 剩下的店铺都是疑难杂症，请配置到黑名单中或联系客服解决，程序即将退出")
                self.browser.close()
                return

            # 如果乱码的有，先乱码等待
            if self.wrong_store_page_count > 0:
                # 二次缓存中已经在黑名单的店铺，那就直接切换标签页进行处理
                wait_refresh_time = self.shop_cfg["wait_refresh_time"]
                loop_for_wait_time = int(wait_refresh_time * 60)
                while loop_for_wait_time:
                    print("\r[%s] [INFO] 挂载乱码店铺中(总时间为%s分钟)，页面还需等待: %s秒" %
                          (
                              time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                              wait_refresh_time,
                              str(loop_for_wait_time)), end=''
                          )
                    time.sleep(1)
                    loop_for_wait_time -= 1

                print("\n[%s] [INFO] 开始刷新页面进行再次尝试乱码页面" %
                      time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                now_handle = self.browser.current_window_handle
                for handles in self.browser.window_handles:
                    if now_handle != handles:
                        self.browser.switch_to.window(handles)
                        self.browser.refresh()
                        time.sleep(3)
                        vender_id = self.browser.current_url[self.browser.current_url.rfind("venderId=") + 9:]
                        for card in self.black_list_shops:
                            if card["brandId"] == vender_id:
                                self.INFO("开始从新标签页注销问题店铺", card["brandName"])
                                if self.close_member(card, self.wrong_store_page_count):
                                    self.wrong_store_page_count -= 1
                                self.browser.close()
                continue

            self.INFO("🧐 本轮运行获取到", len(card_list), "家店铺会员信息")
            for idx, card in enumerate(card_list):
                # 判断本次运行数是否达到设置
                if self.member_close_max_number != 0 and self.member_close_count >= self.member_close_max_number:
                    self.INFO("已注销店铺数达到配置中允许注销的最大次数，程序退出")
                    self.browser.close()
                    return

                # 非指定店铺名字跳过
                if len(self.shop_cfg["specify_shops"]) > 0:
                    if card["brandName"] not in self.shop_cfg["specify_shops"]:
                        self.INFO("发现非指定注销的店铺，跳过", card["brandName"])
                        continue

                # 判断该店铺是否要跳过
                if card["brandName"] in self.need_skip_shops:
                    self.INFO("发现指定需要跳过的店铺，跳过", card["brandName"])
                    self.record_black_list(card)
                    continue

                try:
                    # 打开注销页面
                    if "shopName" in card:
                        self.INFO("开始注销第 %d 家 -> 店铺名: %s 品牌会员名: %s" % (idx + 1, card["shopName"], card["brandName"]))
                    else:
                        self.INFO("开始注销第 %d 家 -> 店铺名: %s 品牌会员名: %s" % (idx + 1, "未知店铺", card["brandName"]))

                    self.browser.get(
                        "https://shopmember.m.jd.com/member/memberCloseAccount?venderId=" + card["brandId"]
                    )

                    # 检查当前店铺退会链接是否失效
                    # noinspection PyBroadException
                    try:
                        WebDriverWait(self.browser, 1).until(EC.presence_of_element_located(
                            (By.XPATH, "//p[text()='网络请求失败']")
                        ))

                        # 云端列表失效页面无需黑名单处理
                        if not state:
                            self.INFO("非当前店铺会员，跳过")
                            continue

                        self.INFO("当前店铺退会链接已失效(缓存导致)，执行清除卡包列表缓存策略后跳过")

                        if card["brandName"] in self.failure_store:
                            self.record_black_list(card)
                            self.failure_store.remove(card["brandName"])
                            self.INFO("当前店铺页面仍然失效，程序加入黑名单后自动跳过")
                            continue
                        else:
                            self.failure_store.append(card["brandName"])
                            self.refresh_cache()
                            continue
                    except Exception as _:
                        pass

                    # 注销具体店铺操作
                    if not self.close_member(card):
                        continue
                except Exception as e:
                    self.ERROR("发生了一点小问题：", e.args)

                    if self.debug:
                        import traceback
                        traceback.print_exc()

            self.INFO("本轮店铺已执行完，即将开始获取下一轮店铺")


if __name__ == '__main__':
    JDMemberCloseAccount().main()
