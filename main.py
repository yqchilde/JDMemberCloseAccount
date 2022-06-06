import copy
import time
import json
import asyncio
import requests
import urllib3

from PIL import Image
from websockets import connect
from captcha.chaojiying import ChaoJiYing
from captcha.tujian import TuJian
from captcha.jd_slide_captcha import JDSlideCaptcha
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


async def ws_conn(ws_conn_url, ws_timeout):
    """
    websocket连接
    """
    async with connect(ws_conn_url) as websocket:
        try:
            recv = await asyncio.wait_for(websocket.recv(), ws_timeout)
            return recv
        except asyncio.TimeoutError:
            return ""


class JDMemberCloseAccount(object):
    """
    京东全自动退店铺会员
    """

    # Info级别日志
    def INFO(self, *args):
        s = ''
        for item in list(map(str, args)):
            s += item
        logger.info("".join(self.pin_name + " >> " + s), stacklevel=2)

    # Warning级别日志
    def WARN(self, *args):
        s = ''
        for item in list(map(str, args)):
            s += item
        logger.warning("".join(self.pin_name + " >> " + s), stacklevel=2)

    # Error级别日志
    def ERROR(self, *args):
        s = ''
        for item in list(map(str, args)):
            s += item
        logger.error("".join(self.pin_name + " >> " + s), stacklevel=2)

    def __init__(self):
        self.pin_name = ''
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

        # 初始化图形验证码配置；滑块（本地过）+ 点选验证码（打码平台过）
        if self.image_captcha_cfg["type"] == "cjy":
            self.cjy = ChaoJiYing(self.image_captcha_cfg)
        elif self.image_captcha_cfg["type"] == "tj":
            self.tj = TuJian(self.image_captcha_cfg)
        elif self.image_captcha_cfg["type"] == "local":
            pass
        elif self.image_captcha_cfg["type"] == "manual":
            pass
        else:
            self.WARN("请在config.yaml中补充image_captcha.type")
            return

        # 初始化店铺变量
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

    # 获取验证码图像
    def get_code_pic(self, name='code_pic.png'):
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

    # 获取加入店铺列表
    def get_shop_cards(self):
        url = "https://api.m.jd.com/client.action?functionId=pg_channel_page_data&clientVersion=10.5.4&build=96906&" \
              "client=android&partner=xiaomi001&eid=eidA29c38122dbscnLOukJcnSxGXmM7q8q4sHJyzsBER4ZMoPHrE1gJtF6wcNbX" \
              "rYg%2Fu9DlsEyMD%2BbaiXUMYwzbRdUPT8JOYhPBQUfPtUNK8aC63XuVO&sdkVersion=25&lang=zh_CN&harmonyOs=0&netwo" \
              "rkType=wifi&uts=0f31TVRjBSvb2atniorYKAvs8QZShfxapqLEl6BaFtR2Ow5FlIKfcOZ%2Fi4Bwd9%2BExyn53J0Yy3KJpl4Q" \
              "z0r3eXiYxrHPVjZiNV56kh5v36F52BYAdI7Vdlphqe%2BIQeQODwtlVcCDkN9IysjqcvcpPNfRjo5ZR7t8YLc%2Fb6l4s8xrx08v" \
              "ra9o6COClMtToR2UK%2FHO5tqrWZlgY0Xs6dZAPg%3D%3D&uemps=0-0&ext=%7B%22prstate%22%3A%220%22%2C%22pvcStu%" \
              "22%3A%221%22%7D&ef=1&ep=%7B%22hdid%22%3A%22JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw%3D%22%2C%22ts" \
              "%22%3A1651377065445%2C%22ridx%22%3A-1%2C%22cipher%22%3A%7B%22osVersion%22%3A%22Dy4nBtS%3D%22%2C%22d_" \
              "brand%22%3A%22WQvrb21f%22%2C%22wifiBssid%22%3A%22ZNOyYJunYJdvZWTtD2O4DNS4ZJOmY2DvCJO4ZNSnDNS%3D%22%2" \
              "C%22screen%22%3A%22CtS2EMenCNqm%22%2C%22d_model%22%3A%22JJSmCNdAC1DN%22%2C%22aid%22%3A%22ZWY2DQPsZNL" \
              "rZtvsCNHwCK%3D%3D%22%2C%22uuid%22%3A%22ZWY2DQPsZNLrZtvsCNHwCK%3D%3D%22%7D%2C%22ciphertype%22%3A5%2C%" \
              "22version%22%3A%221.2.0%22%2C%22appname%22%3A%22com.jingdong.app.mall%22%7D&"

        page_num = 7
        var_name = locals()
        var_name["sign_page1"] = "st=1651377082988&sign=a9c0d37a3975b6484b581e1624ac38b4&sv=121"
        var_name["sign_page2"] = "st=1651377086090&sign=1947fb06fc15c1a7f85088e16a86feb8&sv=121"
        var_name["sign_page3"] = "st=1651377087990&sign=f67f877a27ac152b4d3e2afacdcbe602&sv=112"
        var_name["sign_page4"] = "st=1651377089855&sign=00f8bfcd8cf66f65dc9a2ec7d54a37a0&sv=122"
        var_name["sign_page5"] = "st=1651377091833&sign=203f4bd972015b9c2f6c2456a501c174&sv=100"
        var_name["sign_page6"] = "st=1651377093949&sign=91c080f56e86bf35bb859b1f9bc23360&sv=101"
        var_name["sign_page7"] = "st=1651377096838&sign=0943b62e309cb8c91d9afcebc4b53810&sv=102"

        headers = {
            'Host': 'api.m.jd.com',
            'cookie': self.config["cookie"],
            'charset': 'UTF-8',
            'accept-encoding': 'gzip,deflate',
            'user-agent': self.config["user-agent"][1],
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'content-length': '185'
        }

        card_list = []
        urllib3.disable_warnings()

        for i in range(1, page_num + 1):
            body = "body=%7B%22paramData%22%3A%7B%22pageNum%22%3A{}%2C%22pageSize%22%3A10%2C%22token" \
                   "%22%3A%2201aa0915-9972-425f-8e3d-0d4f0b058cc3%22%7D%2C%22v%22%3A%225.7%22%2C%22v" \
                   "ersion%22%3A1580659200%7D&".format(str(i))
            resp = requests.request(
                "POST",
                url + var_name.get("sign_page" + str(i)), headers=headers, data=body,
                verify=False
            )
            if resp.content:
                ret = json.loads(resp.text)
                if "code" in ret:
                    self.ERROR(ret)
                    break
                else:
                    if ret["data"]["login"]:
                        if not ret["data"]["floorDataValid"]["已领卡楼层"]["content"]:
                            break
                        card_list.extend(ret["data"]["floorInfoList"][0]["floorData"]["content"])
                    else:
                        self.WARN("config.yaml中的cookie值有误，请检查cookie是否失效")
                        return
            else:
                self.ERROR("获取卡包列表接口返回None，请检查网络")
                break

        # 添加店铺名字
        url = "https://ghproxy.fsofso.com/https://github.com/yqchilde/Scripts/blob/main/jd/shop_all.json"
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

    # 利用待领卡接口刷新卡包列表缓存
    def refresh_cache(self):
        url = "https://api.m.jd.com/client.action?functionId=pg_channel_page_data&clientVersion=10.5.4&build=96906&" \
              "client=android&partner=xiaomi001&eid=eidA29c38122dbscnLOukJcnSxGXmM7q8q4sHJyzsBER4ZMoPHrE1gJtF6wcNbX" \
              "rYg%2Fu9DlsEyMD%2BbaiXUMYwzbRdUPT8JOYhPBQUfPtUNK8aC63XuVO&sdkVersion=25&lang=zh_CN&harmonyOs=0&netwo" \
              "rkType=wifi&uts=0f31TVRjBSvb2atniorYKAvs8QZShfxapqLEl6BaFtR2Ow5FlIKfcOZ%2Fi4Bwd9%2BExyn53J0Yy3KJpl4Q" \
              "z0r3eXiYxrHPVjZiNV56kh5v36F52BYAdI7Vdlphqe%2BIQeQODwtlVcCDkN9IysjqcvcpPNfRjo5ZR7t8YLc%2Fb6l4s8xrx08v" \
              "ra9o6COClMtToR2UK%2FHO5tqrWZlgY0Xs6dZAPg%3D%3D&uemps=0-0&ext=%7B%22prstate%22%3A%220%22%2C%22pvcStu%" \
              "22%3A%221%22%7D&ef=1&ep=%7B%22hdid%22%3A%22JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw%3D%22%2C%22ts" \
              "%22%3A1651377065445%2C%22ridx%22%3A-1%2C%22cipher%22%3A%7B%22osVersion%22%3A%22Dy4nBtS%3D%22%2C%22d_" \
              "brand%22%3A%22WQvrb21f%22%2C%22wifiBssid%22%3A%22ZNOyYJunYJdvZWTtD2O4DNS4ZJOmY2DvCJO4ZNSnDNS%3D%22%2" \
              "C%22screen%22%3A%22CtS2EMenCNqm%22%2C%22d_model%22%3A%22JJSmCNdAC1DN%22%2C%22aid%22%3A%22ZWY2DQPsZNL" \
              "rZtvsCNHwCK%3D%3D%22%2C%22uuid%22%3A%22ZWY2DQPsZNLrZtvsCNHwCK%3D%3D%22%7D%2C%22ciphertype%22%3A5%2C%" \
              "22version%22%3A%221.2.0%22%2C%22appname%22%3A%22com.jingdong.app.mall%22%7D&st=1651382963659&sign=2d" \
              "b4445a57da3a46ebe198f8bb714cbb&sv=102"
        body = "body=%7B%22paramData%22%3A%7B%22pageNum%22%3A1%2C%22pageSize%22%3A10%2C%22token%22%3A%2259b136b8-03" \
               "47-493b-a7ce-cd0ee21f98f7%22%7D%2C%22v%22%3A%225.7%22%2C%22version%22%3A1580659200%7D&"
        headers = {
            'Host': 'api.m.jd.com',
            'cookie': self.config["cookie"],
            'charset': 'UTF-8',
            'accept-encoding': 'gzip,deflate',
            'user-agent': self.config["user-agent"][1],
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'content-length': '185'
        }
        urllib3.disable_warnings()
        resp = requests.request("POST", url, headers=headers, data=body, verify=False)
        ret = json.loads(resp.text)
        if "code" in ret:
            self.ERROR(ret)
        else:
            return True

    # 滑块移动
    def slider_move(self, slider, track):
        tracks = []
        current = 0
        mid = track * 4 / 5
        t = 0.7
        v = 0

        while current < track:
            if current < mid:
                a = 2
            else:
                a = -3
            v0 = v
            v = v0 + a * t
            move = v0 * t + 1 / 2 * a * t * t
            current += move
            tracks.append(round(move))

        ActionChains(self.browser).click_and_hold(slider).perform()

        for x in tracks:
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
        time.sleep(0.5)
        ActionChains(self.browser).release().perform()

    # 过滑块验证方法
    def slider_verify(self):
        # 获取元素
        cpc_img_path_base64 = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "(//div[@class='captcha_body']//img)[2]"))).get_attribute('src'). \
            replace("data:image/jpg;base64,", "")
        pcp_show_picture_path_base64 = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//img[@id='cpc_img']/following-sibling::img[1]"))).get_attribute('src'). \
            replace("data:image/png;base64,", "")
        bg = self.browser.find_element(By.XPATH, "(//div[@class='captcha_body']//img)[2]")

        # 正在识别验证码
        self.INFO("正在通过滑块验证识别")
        res = JDSlideCaptcha().detect(cpc_img_path_base64, pcp_show_picture_path_base64)
        if res:
            w1 = bg.size.get("width")
            res = res * w1
            ele = self.browser.find_element(by=By.XPATH, value="//div[@class='bg-blue']/following-sibling::img[1]")
            self.browser.switch_to.window(self.browser.window_handles[0])
            self.slider_move(ele, res)

            # 滑块验证码验证失败尝试重试
            time.sleep(1)
            try:
                if WebDriverWait(self.browser, 1).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@class='sp_msg']//img[1]"))):
                    return False
            except Exception as _:
                self.INFO("检测到滑块验证码切换为点选验证码")
                return True
        else:
            self.INFO("滑块验证识别失败，请反馈给作者")
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@class="jcap_refresh"]'))).click()
            time.sleep(1)
            return False

    # 过点选验证
    def click_on_verify(self):
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

        # 点击确定按钮
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[text()='确定']"))).click()

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

    # 进行具体店铺注销页面的注销操作
    def close_member(self, card):
        # 检查手机尾号是否正确
        phone = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[text()='手机号']/following-sibling::div[1]")
            )
        ).text
        if self.shop_cfg['phone_tail_number'] and phone[-4:] not in self.shop_cfg['phone_tail_number']:
            self.INFO("当前店铺绑定手机号为%s，尾号≠配置中设置的尾号，程序加入黑名单后自动跳过" % phone)
            # 加入黑名单缓存
            if card not in self.black_list_shops:
                self.record_black_list(card)
            return False

        # 发送短信验证码
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//button[text()='发送验证码']")
        ), "发送短信验证码超时 " + card["brandName"]).click()

        # 店铺未开通短信订阅
        # noinspection PyBroadException
        try:
            if WebDriverWait(self.browser, 3).until(EC.presence_of_element_located(
                    (By.XPATH, "//div[text()='店铺未开通短信订阅']"))):
                self.INFO("店铺未开通短信订阅，跳过")
                return False
        except Exception as _:
            pass

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
                    recv = asyncio.run(ws_conn(self.ws_conn_url, self.ws_timeout))
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
            (By.XPATH, "//input[@type='tel']")
        ), "输入短信验证码超时 " + card["brandName"]).send_keys(sms_code)
        time.sleep(1)

        # 点击注销按钮
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[text()='注销会员']")
        ), "点击注销按钮超时 " + card["brandName"]).click()

        # 通过滑块验证或点选验证码
        if self.image_captcha_cfg["type"] == "manual":
            self.INFO("请手动通过滑块验证或点选验证码")
        else:
            # 执行滑块验证
            if not self.slider_verify():
                self.INFO("滑块验证码识别错误，尝试再试一次")
                if not self.slider_verify():
                    self.INFO("滑块验证码识别错误，跳过店铺")
                    return False

            # 执行点选验证码验证
            if not self.click_on_verify():
                self.INFO("点选验证码识别错误，尝试再试一次")
                if not self.click_on_verify():
                    self.INFO("点选验证码识别错误，跳过店铺")
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

    # 记录黑名单店铺
    def record_black_list(self, card):
        if card not in self.black_list_shops:
            self.black_list_shops.append(card)
        if card["brandName"] not in self.need_skip_shops:
            self.need_skip_shops.append(card["brandName"])

    # 移除黑名单店铺
    def remove_black_list(self, card):
        if card in self.black_list_shops:
            self.black_list_shops.remove(card)
        if card["brandName"] in self.need_skip_shops:
            self.need_skip_shops.remove(card["brandName"])

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
                self.pin_name = item.split("=")[1]
        if '%' in self.pin_name:
            import urllib.parse
            self.pin_name = urllib.parse.unquote(self.pin_name)

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
                        if WebDriverWait(self.browser, 1).until(EC.presence_of_element_located(
                                (By.XPATH, "//p[text()='网络请求失败']"))):
                            self.INFO("当前页面无效，跳过")
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
