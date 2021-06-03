"""
京东验证码识别
---
pip3 install numpy, Pillow
---
JDcaptcha(cpc_img_path, pcp_show_picture_path) 传入图片路径
JDcaptcha_base64(cpc_img_path_base64, pcp_show_picture_path_base64) 传入图片base64值
"""
import io

from PIL import Image, ImageDraw
import numpy as np
import base64

# 调整以下几个参数可以有效改变速度与准确度的关系
# 颜色压缩度
GRAIN = 20
# 区块大小
BLOCK = 8
# 压缩倍数
ZOOM = 2


def JDcaptcha(cpc_img_path, pcp_show_picture_path):
    """
    :param cpc_img_path: 大图片地址
    :param pcp_show_picture_path: 需要在大图片中找到的物品图片地址
    :return: 是否成功, (x轴, y轴)
    """
    # Image.open(cpc_img_path).show()
    # Image.open(pcp_show_picture_path).show()

    pcp_show_picture_color = {}
    # (46, 8, 64, 26) 是 验证码主体目标的范围
    pcp_show_picture = Image.open(pcp_show_picture_path).crop(
        (54 - BLOCK / 2, 18 - BLOCK / 2, 54 + BLOCK / 2, 18 + BLOCK / 2))
    # pcp_show_picture.show()
    pcp_show_picture_array = np.array(pcp_show_picture)
    # 减色操作
    for x in range(len(pcp_show_picture_array)):
        for y in range(len(pcp_show_picture_array[x])):
            pcp_show_picture_array[x][y] = [(pcp_show_picture_array[x][y][0] // GRAIN) * GRAIN,
                                            (pcp_show_picture_array[x][y][1] // GRAIN) * GRAIN,
                                            (pcp_show_picture_array[x][y][2] // GRAIN) * GRAIN]
            # 记录颜色
            pcp_show_picture_color[str(pcp_show_picture_array[x][y])] = pcp_show_picture_color.get(
                str(pcp_show_picture_array[x][y]), 0) + 1
    pcp_show_picture_target = max(pcp_show_picture_color, key=pcp_show_picture_color.get)
    pcp_show_picture_count = pcp_show_picture_color[max(pcp_show_picture_color, key=pcp_show_picture_color.get)]

    # 处理大图片
    cpc_img_path_max_probability = 0
    # (0, 275)为图片的 x 轴像素， (0, 170)为图片的 y 轴的像素
    for row in range(0, 275, int(BLOCK / 2)):
        for col in range(0, 170, int(BLOCK / 2)):
            cpc_img = Image.open(cpc_img_path).crop((row, col, row + BLOCK, col + BLOCK))
            cpc_img_color = {}

            # 减少图片分辨率减少处理计算量
            width, height = cpc_img.size
            cpc_img.thumbnail((width // ZOOM, height // ZOOM))

            cpc_img_array = np.array(cpc_img)

            for x in range(len(cpc_img_array)):
                for y in range(len(cpc_img_array[x])):
                    cpc_img_array[x][y] = [(cpc_img_array[x][y][0] // GRAIN) * GRAIN,
                                           (cpc_img_array[x][y][1] // GRAIN) * GRAIN,
                                           (cpc_img_array[x][y][2] // GRAIN) * GRAIN]

                    # 记录颜色
                    cpc_img_color[str(cpc_img_array[x][y])] = cpc_img_color.get(str(cpc_img_array[x][y]), 0) + 1

            if max(cpc_img_color, key=cpc_img_color.get) == pcp_show_picture_target:
                if cpc_img_color[
                    max(cpc_img_color, key=cpc_img_color.get)] / pcp_show_picture_count > cpc_img_path_max_probability:
                    target_x, target_y = row, col
                # print((max(cpc_img_color, key=cpc_img_color.get), row, col))

    try:
        if __name__ == '__main__':
            im = Image.open(cpc_img_path)
            draw = ImageDraw.Draw(im)
            draw.rectangle((target_x, target_y, target_x + BLOCK, target_y + BLOCK), outline='red', width=1)
            im.show()
        return True, (int((2 * target_x + BLOCK) / 2), int((2 * target_y + BLOCK) / 2))
    except (KeyError, NameError):
        return False, (None, None)


def JDcaptcha_base64(cpc_img_path_base64, pcp_show_picture_path_base64):
    """
    :param cpc_img_path_base64: 主图片 base64
    :param pcp_show_picture_path_base64: 目标图片 base64
    :return:
    """
    return JDcaptcha(io.BytesIO(base64.b64decode(cpc_img_path_base64.replace("data:image/jpg;base64,", ""))),
                     io.BytesIO(base64.b64decode(pcp_show_picture_path_base64.replace("data:image/jpg;base64,", ""))))


if __name__ == '__main__':
    # 测试图片集就不附上了
    # 如果需要自行测试的话保存类似：原图：1-1.jpg 目标1-2.jpg
    for i in range(1, 21):
        # 普通测试
        print(JDcaptcha("img/" + str(i) + "-1.jpg", "img/" + str(i) + "-2.jpg"))
        # 测试 base64
        print(JDcaptcha_base64(base64.b64encode(open("img/" + str(i) + "-1.jpg", "rb").read()),
                               base64.b64encode(open("img/" + str(i) + "-2.jpg", "rb").read())))
