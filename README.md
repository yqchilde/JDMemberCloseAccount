# JDMemberCloseAccount

## 介绍

本项目是我学习python操作selenium的一个🌰，也是一种京东自动退会方案，用来全自动退出京东加入的所有店铺会员

## 声明

1. 本项目仅限于学习研究selenium库的操作，以及一些python知识

## 须知

1. 有一定的电脑知识 or 有耐心爱折腾
2. chrome驱动(只在chrome测试了，故只留了chrome)
3. 操作系统(只在mac上测试了，非M1)
4. 使用`python3.x`版本执行
5. 有一定python基础知识，没有的话先去学一下，起码得会搭python环境

## 思路

![项目思路](https://github.com/yqchilde/JDMemberCloseAccount/blob/main/screenshots/project_1.png)

1. 利用selenium打开退会页面

2. 第一关：手机验证码

    1. 安卓端（以下两种任选一个用就行）：

        * 利用[macrodroid软件](https://wwa.lanzoui.com/iLeAYps1x1i) 监听，一旦监听到就立即通过HTTP请求利用websocket推送过来，由`jd_wstool`
          工具监听并送到selenium中填写

        * 利用[macrodroid软件](https://wwa.lanzoui.com/iSwocpqow3a) 监听，一旦监听到就立即通过HTTP请求利用websocket推送过来，由`jd_wstool`
          工具监听并送到selenium中填写

        * 利用[tasker软件](https://wwa.lanzoui.com/iLeAYps1x1i) 监听，同上

        * 关于 `tasker` 和 `macrodroid` 配置均在 [extra](https://github.com/yqchilde/JDMemberCloseAccount/tree/main/extra) 目录下

    2. ios端：

        1. 越狱机（来自[@curtinlv](https://github.com/curtinlv)
           大佬的越狱监听短信方法，[#61](https://github.com/yqchilde/JDMemberCloseAccount/pull/61) ）

            * 像安卓端一样传验证码（基本逻辑：iOS设备通过访问短信数据库，监听最新的jd验证码并传到 `jd_wstool`）

                1.
                下载 [getiOSMessages.py](https://github.com/yqchilde/JDMemberCloseAccount/blob/main/extra/iOSPlus/getiOSMessages.py)
                传到手机上（测试Pythonista 3可以，其他软件自行研究）

                2. 填写`jd_wstool` 监听地址ip

                   如：监听地址1： http://192.168.0.101:5201，填在脚本开头 ipaddr= '192.168.0.101'

                3. 运行脚本

        2. 非越狱机 （任选以下一种类型）

           > 首先感谢tg群的朋友[@millerchen](https://github.com/bluewatercg)
           提供的思路，具体实现方案是电脑屏幕留出一个区域用来显示手机投屏的地方，然后打开短信列表，然后找个截图工具记一下当前需要识别的的`左上角`和`右下角`坐标(最好截取那一整条短信的坐标，当然截取范围越小，识别越快)，然后通过ocr工具识别数字验证码

           > **注意：** OCR只是处理识别短信验证码并填入，不要误解为图形验证码也可以解决。如果定位不准，看一下项目目录生成的`ios_code_pic.png`
           图片位置在当前屏幕的哪个位置，[测试识别效果gif点我查看](https://github.com/yqchilde/JDMemberCloseAccount#screenshots) , 此外，坐标和电脑分辨率有关，如果分辨是是1080P，那么qq截图识别的坐标就是刚好一比一的，比我的是4k显示器，是以百分之200显示的，那所有坐标就要乘以2了

           百度ocr (
           之前用过的用户还是免费500次/天的额度，新用户调整为1000次/月的额度，调整详情参考[这里](https://ai.baidu.com/support/news?action=detail&id=2390))

                * 需要在`config.yaml`中配置如下参数：

                * `sms_captcha.is_ocr`设置为`true`

                * `sms_captcha.is_ocr.type`设置为`baidu`

                * `sms_captcha.is_ocr.baidu_app_id`补充完整

                * `sms_captcha.is_ocr.baidu_api_key`补充完整

                * `sms_captcha.is_ocr.baidu_secret_key`补充完整

           阿里云ocr (
           用户新购0元500次，后续500次/0.01元，开通地址[阿里云市场](https://market.aliyun.com/products/57124001/cmapi028554.html?spm=5176.2020520132.101.2.608172181RzlnC#sku=yuncode2255400000))

                * 同上，需要在`config.yaml`中配置如下参数：

                * `sms_captcha.is_ocr`设置为`true`

                * `sms_captcha.is_ocr.type`设置为`aliyun`

                * `sms_captcha.is_ocr.aliyun_appcode`补充完整

           easyocr (免费，本地识别)

                * 同上，需要在`config.yaml`中配置如下参数：

                * `sms_captcha.is_ocr`设置为`true`

                * `sms_captcha.is_ocr.type`设置为`easyocr`

                * 使用时注意框选识别的范围只显示6位数字验证码(现支持一整条完整短信的区域，当然范围越大识别速度也会相应增加，区域扩大是为了优化某些用户短信验证码6位数字每次位置不一致问题)（毕竟免费开源，识别条件有点苛刻）

3. 第二关：图形验证码（任选以下一种类型，默认采用本地识别）

    1. 本地识别（再也不用花钱了👍），来自[@AntonVanke](https://github.com/AntonVanke)
       大佬提供的 [JDCaptcha](https://github.com/AntonVanke/JDCaptcha) 项目(已集成)
       ，[测试图在最后一张](https://github.com/yqchilde/JDMemberCloseAccount#screenshots) ，

    2. 收费的打码平台

        * 图形验证码用 [超级鹰打码](https://www.chaojiying.com/) ，费用是1块=1000积分，一次扣15积分

        * 图形验证码用 [图鉴打码](http://www.ttshitu.com/) ，费用是1块=1积分，一次扣0.01积分

## 操作

### 1. 下载项目以及配置浏览器驱动

**注意：** 以下关于`python3`， `pip3` 命令只代表`python3.x`环境，故如果电脑`python`环境已是3.x，可直接用`python`、`pip`代替

1. 克隆到本地或下载项目压缩包到本地

   ```shell
   git clone https://github.com/yqchilde/JDMemberCloseAccount.git
   ```

2. 在项目根目录下打开终端执行以下命令，安装所需要的包

   ```shell
   pip3 install -r requirements.txt
   ```

3. 下载对应的浏览器驱动放到项目的`drivers`文件夹下面

    * `chrome`请访问`chrome://version/`查看浏览器的版本，然后去 [chromedriver](http://chromedriver.storage.googleapis.com/index.html)
      下载对应的版本/系统驱动（只需要保证版本号前三段一致即可，比如`91.0.4472.77`只需要保证`91.0.4472.x`就行），下载后解压，将其可执行文件（mac为`chromedriver`
      ，win为`chromedriver.exe`放在项目的`drivers`目录下即可）

### 2. 补充配置文件

* `config.yaml`文件

```yaml
# 手机端cookie，是pt_key=xxx;pt_pin=xxx;
cookie: ""
debug: false

# selenium 相关
# selenium.browserType: 浏览器类型
# selenium.headless: 无头模式，建议默认设置
# selenium.binary: 可执行路径，如果驱动没有找到浏览器的话需要你手动配置
# selenium.selenium_timeout: selenium操作超时时间，超过会跳过当前店铺，进行下一个店铺，默认为30秒
selenium:
  browserType: "Chrome"
  headless: false
  binary: ""
  selenium_timeout: 30

# shop 店铺设置相关
# shop.skip_shops: 需要跳过的店铺，需要填写卡包中的完整店铺名称，为了效率没做模糊匹配，多个店铺用逗号隔开
# shop.phone_tail_number: 手机后4位尾号，若填写将会校验店铺尾号是否是规定的，不符合就跳过
# shop.member_close_max_number: 设置本次运行注销的最大店铺数，默认为0，代表不限制
shop:
  skip_shops: ""
  phone_tail_number: ""
  member_close_max_number: 0

# sms_captcha 短信验证码相关
# sms_captcha.is_ocr: 是否开启OCR模式，IOS设备必须开启，安卓非必须
# sms_captcha.ws_conn_url: websocket链接地址，不用动
# sms_captcha.ws_timeout: websocket接收验证码时间超时时间，超时会跳过当前店铺，进行下一个店铺，默认为60秒
# sms_captcha.ocr.type: ocr的类型，可选：baidu、aliyun、easyocr
# sms_captcha.ocr.ocr_range: 需要截取的投屏区域的验证码左上角和右下角坐标，顺序依次是 [左x,左y,右x,右y]，如[1,2,3,4]
# sms_captcha.ocr.ocr_delay_time: OCR识别的延迟时间，如果没识别到就几秒后再次尝试，默认为5
# sms_captcha.ocr.baidu_app_id: 需要在[百度智能云](https://cloud.baidu.com/) 注册个账号，搜索文字识别项目，创建应用后的`app_id`
# sms_captcha.ocr.baidu_api_key: 需要在[百度智能云](https://cloud.baidu.com/) 注册个账号，搜索文字识别项目，创建应用后的`api_key`
# sms_captcha.ocr.baidu_secret_key: 需要在[百度智能云](https://cloud.baidu.com/) 注册个账号，搜索文字识别项目，创建应用后的`secret_key`
# sms_captcha.ocr.aliyun_appcode: 需要在[阿里云市场](https://market.aliyun.com/products/57124001/cmapi028554.html?spm=5176.2020520132.101.2.608172181RzlnC#sku=yuncode2255400000) 购买后的`AppCode`
sms_captcha:
  is_ocr: false
  ws_conn_url: "ws://localhost:5201/subscribe"
  ws_timeout: 60
  ocr:
    type: ""
    ocr_range: [ ]
    ocr_delay_time: 10
    baidu_app_id: ""
    baidu_api_key: ""
    baidu_secret_key: ""
    aliyun_appcode: ""

# image_captcha 图形验证码相关
# image_captcha.type: 图形验证码类型，可选：local、cjy、tj
# image_captcha.cjy_username: 超级鹰账号，仅在 image_captcha.type 为 cjy 时需要设置
# image_captcha.cjy_password: 超级鹰密码，仅在 image_captcha.type 为 cjy 时需要设置
# image_captcha.cjy_soft_id: 超级鹰软件ID，仅在 image_captcha.type 为 cjy 时需要设置
# image_captcha.cjy_kind: 超级鹰验证码类型，仅在 image_captcha.type 为 cjy 时需要设置，且该项目指定为 9101
# image_captcha.tj_username: 图鉴账号，仅在 image_captcha.type 为 tj 时需要设置
# image_captcha.tj_password: 图鉴密码，仅在 image_captcha.type 为 tj 时需要设置
# image_captcha.tj_type_id: 图鉴验证码类型，仅在 image_captcha.type 为 tj 时需要设置，且该项目指定为 19
image_captcha:
  type: "local"
  cjy_username: ""
  cjy_password: ""
  cjy_soft_id: ""
  cjy_kind: 9101
  tj_username: ""
  tj_password: ""
  tj_type_id: 19

# user-agent 用户代理，可自行配置
user-agent:
  - Mozilla/5.0 (Linux; Android 11; M2007J3SC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36
  - okhttp/3.12.1;jdmall;android;version/10.0.2;build/88569;screen/1080x2266;os/11;network/wifi;
```

### 3. 添加`cookie` （二选一）

* 使用`add_cookie.py`可以获取手机端`Cookie` 并自动配置到 `config.yaml` 文件中

* 手动在 `config.yaml` 中写入 `cookie` 项，注意是pt_key=123456;pt_pin=jd_987654的那个（**请不要随意泄露你的cookie**）

### 4. 根据手机终端类型补充配置 （其实还是第2步，这里详细再讲下）

大体说一下，这块是关于手机端短信验证码的配置

1. 安卓推荐使用tasker或macrodroid，不要用ocr，不必须，是为了你省事，IOS越狱设备也可以使用短信转发功能，IOS非越狱必须使用OCR

2. 如果是使用tasker / macrodroid，is_ocr肯定是false，代表不用ocr

3. 如果用ocr，is_ocr写true，能理解吧

4. ocr里面的type是三选一，baidu / aliyun / easyocr，代表你要用的ocr平台是哪个，easyocr是本地的，其他两个是线上的

5. ocr_range是你要截图的区域，不知道怎么截，往下翻，有截图

6. ocr_delay_time是ocr延迟时间，不想改就保持默认

7. 下面的配置，就是type你用baidu，下面id，key啥的你就写baidu的，阿里同样原理，easyocr不用写

### 5. 启动 [jd_wstool](https://github.com/yqchilde/JDMemberCloseAccount/releases) 工具（使用OCR的不用开）

这个步骤只需要安卓端手机用了tasker 或 macrodroid 或其他自动化工具的开启

什么意思呢？就是配置文件中你的 `is_ocr`为false的，就要开启，否则不用开启

### 6. 启动主程序

在项目目录下执行`python3 main.py`，等待执行完毕即可

## 关于 `jd_wstool` 工具

该工具是用来监听手机端发送HTTP请求传递验证码的，实现原理是websocket

1. 我编译好了各种操作系统的包，直接下载 [jd_wstool](https://github.com/yqchilde/JDMemberCloseAccount/releases), 选择自己的电脑系统对应的压缩包，解压运行
2. 自行编译，代码在 [cmd](https://github.com/yqchilde/JDMemberCloseAccount/tree/main/cmd) 目录下

## 常见问题

1. Tasker | Macrodroid 监听不到短信怎么办？

    * vivo手机和iqoo手机的验证码保护取消： 短信-设置-隐私保护-验证码安全保护关闭

    * 小米手机：权限-允许读取短信 & 允许读取通知类短信

    * 华为手机：短信-右上角三个点-设置-验证码安全保护关闭

    * 权限没问题的，看下tasker的日志或macrodroid的日志，有错误会显示

2. 百度OCR报错 `{'error_code': 18, 'error_msg': 'Open api qps request limit reached'}`

    * 答案在这里 https://github.com/yqchilde/JDMemberCloseAccount/issues/48

3. 百度OCR报错 `{'error_code': 14, 'error_msg': 'IAM Certification failed'}`

    * 说明从百度复制到配置文件的`baidu_app_id`, `baidu_api_key`, `baidu_secret_key` 不正确

## 测试

1. websocket转发验证码

    1. 电脑运行`python3 test_main.py` 和 `./jd_wstool` 工具，windows记得 `.exe` ，此时模拟启动main程序和监听验证码程序
    2. 手机访问 `http://你的IP:5201/publish?smsCode=1234522`，之后查看电脑上`jd_wstool` 和 `test_main.py` 的控制台输出信息

2. 百度OCR

    1. 运行`python3 ./captcha/baidu_ocr.py`测试

3. Easy OCR

    1. 运行`python3 ./captcha/easy_ocr.py`测试

## ScreenShots

<div align=center>
<img src="https://github.com/yqchilde/JDMemberCloseAccount/blob/main/screenshots/test_img1.gif" width="600" />
</div>

<div align=center>
<img src="https://github.com/yqchilde/JDMemberCloseAccount/blob/main/screenshots/test_img2.gif" width="600" />
</div>

<div align=center>
<img src="https://github.com/yqchilde/JDMemberCloseAccount/blob/main/screenshots/test_img3.png" width="600" />
</div>

<div align=center>
<img src="https://github.com/yqchilde/JDMemberCloseAccount/blob/main/screenshots/test_img4.png" width="800" />
</div>

<div align=center>
<img src="https://github.com/yqchilde/JDMemberCloseAccount/blob/main/extra/iOSPlus/test.png" width="600" />
</div>

## TG讨论群

[JD退会讨论群 https://t.me/jdMemberCloseAccount](https://t.me/jdMemberCloseAccount)

# Thanks

感谢以下作者开源JD相关项目供我学习使用

[@AntonVanke](https://github.com/AntonVanke/JDBrandMember)

