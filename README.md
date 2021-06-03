# JDMemberCloseAccount

学习python操作selenium的一个🌰，用来 全自动/半自动 退出加入的所有店铺会员

* 全自动：短信验证码全自动，图形验证码任选下面的一种，我测试图鉴比较好，又便宜又速度快

  * 图形验证码用 [超级鹰打码](https://www.chaojiying.com/) ，费用是1块=1000积分，一次扣15积分

  * 图形验证码用 [图鉴打码](https://www.ttshitu.com/) ，费用是1块=1积分，一次扣0.01积分

  * 图形验证码用 本地识别引擎，识别效率和精准度可能不会很高 [测试图最后一张](https://github.com/yqchilde/JDMemberCloseAccount#screenshots) (感谢 [@AntonVanke](https://github.com/AntonVanke) )的 PR，这下大家可以不用花钱了👍

  * **当`cjy_validation` 和 `tj_validation` 都为false时，启动本地引擎识别**

* 半自动：短信验证码全自动，图形验证码手动

## 要求

1. 有一定的电脑知识 or 有耐心爱折腾
   
2. chrome驱动(只在chrome测试了，故只留了chrome)
   
3. 操作系统(只在mac上测试了，非M1)
   
4. 关于手机短信验证码同步到浏览器中，本人采用了websocket来传递验证码
   
5. 关于如何在手机传递到浏览器，这点只说一下我的方式(达到目的即可)
   
   * 安卓端：利用tasker软件监听，一旦监听到就立即通过websocket推送过来
   
   * 安卓端：利用macrodroid软件监听，一旦监听到就立即通过websocket推送过来
   
   * 关于 `tasker` 和 `macrodroid` 配置均在 [extra](https://github.com/yqchilde/JDMemberCloseAccount/tree/main/extra) 目录下
   
   * ios端：首先感谢tg群的朋友[@millerchen](https://github.com/bluewatercg) 提供的思路，具体实现方案是电脑屏幕留出一个区域用来显示手机投屏的地方，然后打开短信列表，然后找个截图工具记一下当前需要识别的的左上角和右下角坐标(最好能暴露出完整短信)，再利用[百度ocr](https://cloud.baidu.com/product/ocr_general?track=navigation0904) 识别，识别到后获取结果并输入，百度ocr一个账号一天免费500次调用
   
   * <span style="color: red; "> 注意：百度OCR只是处理识别短信验证码并填入，不要误解为图形验证码也可以解决 </span>
   
   * 如果定位不准，看一下项目目录生成的`ios_code_pic.png`图片位置在当前屏幕的哪个位置，[识别效果gif](https://github.com/yqchilde/JDMemberCloseAccount#screenshots) 
     此外，坐标和电脑分辨率有关，如果分辨是是1080P，那么qq截图识别的坐标就是刚好一比一的，比我的是4k显示器，是以百分之200显示的，那所有坐标就要乘以2了。

## 安装方法

1. 克隆到本地

    ```shell
    git clone https://github.com/yqchilde/JDMemberCloseAccount.git
    ```

2. 安装所需要的包

    ```shell
    pip3 install -r requirements.txt
    ```

3. 下载对应的浏览器驱动放到项目的`drivers`文件夹下面
    * `chrome`请访问`chrome://version/`查看浏览器的版本，然后去 [chromedriver](http://chromedriver.storage.googleapis.com/index.html) 下载对应的版本/系统驱动

4. 配置`config.json`

    ```json
    {
        "device": "",
        "baidu_app_id": "",
        "baidu_api_key": "",
        "baidu_secret_key": "",
        "baidu_range": [1231,393,1383,412],
        "baidu_delay_time": 5,
        "browserType": "Chrome",
        "headless": false,
        "binary": "",
        "cjy_validation": false,
        "cjy_username": "",
        "cjy_password": "",
        "cjy_soft_id": "",
        "cjy_kind": 9101,
        "tj_validation": false,
        "tj_username": "",
        "tj_password": "",
        "tj_type_id": 19,
        "ws_conn_url": "ws://localhost:5201/subscribe",
        "ws_timeout": 60,
        "selenium_timeout": 30,
        "skip_shops": "",
        "phone_tail_number": "",
        "member_close_max_number": 0,
        "mobile_cookie": "",
        "users": {}
    }
    ```

    * `device`: 如果是ios设备就填写ios，安卓留空
      
    * `baidu_app_id`: 需要在[百度智能云](https://cloud.baidu.com/) 注册个账号，搜索文字识别项目，创建应用后的`app_id`
      
    * `baidu_api_key`: 需要在[百度智能云](https://cloud.baidu.com/) 注册个账号，搜索文字识别项目，创建应用后的`api_key`
      
    * `baidu_secret_key`: 需要在[百度智能云](https://cloud.baidu.com/) 注册个账号，搜索文字识别项目，创建应用后的`secret_key`
      
    * `baidu_range`: 需要截取的投屏区域的验证码左上角和右下角坐标，顺序依次是 [左x,左y,右x,右y]
     
    * `baidu_delay_time`: 百度OCR识别的延迟时间，如果没识别到就几秒后再次尝试，默认为5
      
    * `browserType`: 浏览器类型
    
    * `headless`: 无头模式，建议默认设置
    
    * `binary`: 可执行路径，如果驱动没有找到浏览器的话需要你手动配置
    
    * `cjy_validation`: 是否开启超级鹰验证图形验证码
    
    * `cjy_username`: 超级鹰账号，仅在 cjy_validation 为 true 时需要设置
    
    * `cjy_password`: 超级鹰密码，仅在 cjy_validation 为 true 时需要设置
    
    * `cjy_soft_id`: 超级鹰软件ID，仅在 cjy_validation 为 true 时需要设置

    * `cjy_kind`: 超级鹰验证码类型，仅在 cjy_validation 为 true 时需要设置，且该项目指定为 `9101`

    * `tj_validation`: 是否开启图鉴验证图形验证码
   
    * `tj_username`: 图鉴账号，仅在 tj_validation 为 true 时需要设置
   
    * `tj_password`: 图鉴密码，仅在 tj_validation 为 true 时需要设置
   
    * `tj_type_id`: 超级鹰验证码类型，仅在 tj_validation 为 true 时需要设置，且该项目指定为 `19`
    
    * `ws_conn_url`: websocket链接地址，不用动
      
    * `ws_timeout`: websocket接收验证码时间超时时间，超时会跳过当前店铺，进行下一个店铺，默认为60秒
   
    * `selenium_timeout`: selenium操作超时时间，超过会跳过当前店铺，进行下一个店铺，默认为30秒
   
    * `skip_shops`: 需要跳过的店铺，需要填写卡包中的完整店铺名称，为了效率没做模糊匹配，多个店铺用逗号隔开
   
    * `phone_tail_number`: 手机后4位尾号，若填写将会校验店铺尾号是否是规定的，不符合就跳过
   
    * `member_close_max_number`: 设置本次运行注销的最大店铺数
    
    * `mobile_cookie`: 手机端cookie，是pt_key开头的那个
    
    * `users`: web端cookie，通过add_cookie.py添加


5.  添加`cookie`

    * web端cookie：请在项目目录下执行`python3 add_cookie.py`， 在打开的浏览器界面登录你的京东，此时你可以看到`config.json`已经有了你的用户信息（**请不要随意泄露你的cookie**）
      
    * 手机端cookie：在 `config.json` 中写入 `mobile_cookie` 项，注意是pt_key开头的那个（**请不要随意泄露你的cookie**）

6.  执行主程序

    在项目目录下执行`python3 main.py`，等待执行完毕即可

## websocket服务端运行(以下两种方法任一都行，图省事就用2)

1. 手动运行 `go run ./cmd/jd_wstool`

2. 下载 [jd_wstool](https://github.com/yqchilde/JDMemberCloseAccount/releases), 选择自己的电脑系统对应的压缩包，解压运行

![测试图](https://github.com/yqchilde/JDMemberCloseAccount/blob/main/screenshots/test_img3.png)

## 手机端短信如何传递给电脑端

1. 安卓端，我是用了tasker监听，总是随便一个可以监听到的，然后请求接口就行，接口如下

2. 安卓端，用 `Macrodroid监听`，原理一样

   * 关于 `tasker` 和 `macrodroid` 配置均在 [extra](https://github.com/yqchilde/JDMemberCloseAccount/tree/main/extra) 目录下

3. ios端，找一个投屏软件，群友教程提供的是 [airplayer](https://pro.itools.cn/airplayer), 然后记录验证码区域坐标，通过百度ocr识别并填入

```bash
http://同局域网IP:5201/publish?smsCode=短信验证码

例如：
http://192.168.2.100:5201/publish?smsCode=12345

同局域网IP会在运行 `./jd_wstool 或 jd_wstool.exe` 时提示出来，例如：
listening on http://192.168.2.100:5201
```

## 常见问题

1. Tasker | Macrodroid 监听不到短信怎么办？

   * vivo手机和iqoo手机的验证码保护取消： 短信-设置-隐私保护-验证码安全保护关闭
   
   * 小米手机：权限-允许读取短信 & 允许读取通知类短信
   
   * 华为手机：短信-右上角三个点-设置-验证码安全保护关闭

## 测试

1. websocket转发验证码
   
   1. 电脑运行`python3 test_main` 和 `./jd_wstool` 工具，windows记得 `.exe` ，此时模拟启动main程序和监听验证码程序
   2. 手机访问 `http://你的IP:5201/publish?smsCode=1234522`，之后查看电脑上`jd_wstool` 和 `test_main.py` 的控制台输出信息

## ScreenShots

![测试图1](https://github.com/yqchilde/JDMemberCloseAccount/blob/main/screenshots/test_img1.gif)

![测试图2](https://github.com/yqchilde/JDMemberCloseAccount/blob/main/screenshots/test_img2.gif)

![测试图3](https://github.com/yqchilde/JDMemberCloseAccount/blob/main/screenshots/test_img3.gif)

![测试图4](https://github.com/yqchilde/JDMemberCloseAccount/blob/main/screenshots/test_img4.png)

# Thanks

感谢以下作者开源JD相关项目供我学习使用

[@AntonVanke](https://github.com/AntonVanke/JDBrandMember)

