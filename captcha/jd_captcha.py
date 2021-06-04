"""
京东验证码识别
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
GRAIN = 16
# 区块大小
BLOCK = 16
# 压缩倍数
ZOOM = 3


def JDcaptcha(cpc_img_path, pcp_show_picture_path):
    """
    :param cpc_img_path: 大图片地址
    :param pcp_show_picture_path: 需要在大图片中找到的物品图片地址
    :return: 是否成功, (x轴, y轴)
    """
    pcp_show_picture_color = {}

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

    # print(pcp_show_picture_color)
    pcp_show_picture_color_list = list(pcp_show_picture_color)

    # 处理大图片
    cpc_img_path_max_probability = {}
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
                    # print(len(cpc_img_array)*len(cpc_img_array[x]))
                    # 记录颜色
                    cpc_img_color[str(cpc_img_array[x][y])] = cpc_img_color.get(str(cpc_img_array[x][y]), 0) + 1
            for _ in cpc_img_color:
                if _ in pcp_show_picture_color_list:
                    cpc_img_path_max_probability[str([row, col])] = cpc_img_path_max_probability.get(str([row, col]),
                                                                                                     0) + 1

    target_x, target_y = eval(max(cpc_img_path_max_probability, key=cpc_img_path_max_probability.get))[0], \
                         eval(max(cpc_img_path_max_probability, key=cpc_img_path_max_probability.get))[1]

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
    pass
    # import time
    #
    # # 8:16:2  20 28 32 19 20
    # # 16:16:3 47 54 55
    # start_time = time.time()
    #
    # count = 0
    # try:
    #     for i in range(41, 61):
    #         # 普通测试
    #         print(JDcaptcha("img/" + str(i) + "-1.jpg", "img/" + str(i) + "-2.jpg"))
    #
    #         # 测试 base64
    #         # print(JDcaptcha_base64(base64.b64encode(open("img/" + str(i) + "-1.jpg", "rb").read()),
    #         #                        base64.b64encode(open("img/" + str(i) + "-2.jpg", "rb").read())))
    #         count += 1
    #
    #
    # except:
    #     pass
    # finally:
    #     end_time = time.time()
    #     print("总时长{},共{}个图片, 平均时长{}每图".format(end_time - start_time, count, (end_time - start_time) / count))
