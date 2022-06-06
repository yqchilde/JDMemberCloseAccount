from utils.config import get_config

key_list = [
    "cookie",
    "debug",
    "selenium.browserType",
    "selenium.headless",
    "selenium.binary",
    "selenium.timeout",
    "selenium.check_wait",
    "shop.skip_shops",
    "shop.specify_shops",
    "shop.phone_tail_number",
    "shop.member_close_max_number",
    "sms_captcha.is_ocr",
    "sms_captcha.jd_wstool",
    "sms_captcha.ws_conn_url",
    "sms_captcha.ws_timeout",
    "sms_captcha.ocr",
    "sms_captcha.ocr.type",
    "sms_captcha.ocr.ocr_range",
    "sms_captcha.ocr.ocr_delay_time",
    "sms_captcha.ocr.baidu_app_id",
    "sms_captcha.ocr.baidu_api_key",
    "sms_captcha.ocr.baidu_secret_key",
    "sms_captcha.ocr.baidu_fanyi_appid",
    "sms_captcha.ocr.baidu_fanyi_appkey",
    "sms_captcha.ocr.aliyun_appcode",
    "image_captcha.type",
    "image_captcha.cjy_username",
    "image_captcha.cjy_password",
    "image_captcha.cjy_soft_id",
    "image_captcha.cjy_kind",
    "image_captcha.tj_username",
    "image_captcha.tj_password",
    "image_captcha.tj_type_id",
    "user-agent",
]


def verify_configuration(logger):
    """
    检查config.yaml配置是否正常
    """
    config = get_config()
    missing_key = []

    for key in key_list:
        point_count = key.count(".")
        if point_count == 0:
            if key not in config:
                missing_key.append(key)
        elif point_count == 1:
            _key_ = key.split(".", 1)
            if _key_[0] in missing_key:
                missing_key.append(key)
                continue
            if config[_key_[0]] is None or _key_[1] not in config[_key_[0]]:
                missing_key.append(key)
        elif point_count == 2:
            _key_ = key.split(".", 2)
            if _key_[0] in missing_key or _key_[0] + "." + _key_[1] in missing_key:
                missing_key.append(key)
                continue
            if config[_key_[0]][_key_[1]] is None or _key_[2] not in config[_key_[0]][_key_[1]]:
                missing_key.append(key)

    if missing_key:
        logger.info("配置文件(config.yaml)中缺少键%s，请检查配置文件" % missing_key)
        exit(1)
