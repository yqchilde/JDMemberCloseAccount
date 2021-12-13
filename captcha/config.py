from PIL import ImageGrab

# 验证码图片名字
captcha_screenshot = "captcha_screenshot.png"

# 6位数字短信验证码正则匹配规则
matching_rules = [
    r'\'[\d]{6}\'',
    r'([\d]{6})[\u3002]',
    r'([\d]{6})[\uff0c]',
    r'(您的验证码为[\d]{6})',
    r'([\d]{6}),',
    r'[\d]{6}',
]


# 获取验证码图像
def screenshot_save(_range_, name='captcha_screenshot.png'):
    # 根据验证码的左上角坐标和右下角坐标截图
    code_pic = ImageGrab.grab(_range_)
    code_pic.save(name)
    return code_pic
