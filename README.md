# JDMemberCloseAccount
学习python操作selenium的一个🌰，用来 全自动/半自动 退出加入的所有店铺会员

该项目操作有一定复杂度，如果无法看懂还是请找寻其他解决方案，比如websocket的服务端未提供，因为这个不重要，随便跑一个websocket的Server端Demo
能做到通信即可，故本项目也可以说是给出了自动退会的一种方案

## 要求

1. 有一定的电脑知识 or 有耐心爱折腾
   
2. chrome驱动(只在chrome测试了，故只留了chrome)
   
3. 操作系统(只在mac上测试了，非M1)
   
4. 关于手机短信验证码同步到浏览器中，本人采用了websocket来传递验证码，注意websocket传递验证码格式为 `{"sms_code": "123456"}`
   
5. 关于如何在手机传递到浏览器，这点只说一下我的方式(达到目的即可)
   
   * 安卓端：利用tasker软件监听，一旦监听到就立即通过websocket推送过来

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
        "browserType": "Chrome",
        "headless": false,
        "binary": "",
        "cjy_validation": false,
        "cjy_username": "",
        "cjy_password": "",
        "cjy_soft_id": "",
        "cjy_kind": 9101,
        "ws_conn_url": "ws://localhost:5213/ws?user_id=123",
        "mobile_cookie": "",
        "users": {}
    }
    ```
   
    * `browserType`: 浏览器类型
    
    * `headless`: 无头模式，建议默认设置
    
    * `binary`: 可执行路径，如果驱动没有找到浏览器的话需要你手动配置
    
    * `cjy_validation`: 是否开启超级鹰验证图形验证码
    
    * `cjy_username`: 超级鹰账号，仅在 cjy_validation 为 True 时需要设置
    
    * `cjy_password`: 超级鹰密码，仅在 cjy_validation 为 True 时需要设置
    
    * `cjy_soft_id`: 超级鹰软件ID，仅在 cjy_validation 为 True 时需要设置
    
    * `cjy_kind`: 超级鹰验证码类型，仅在 cjy_validation 为 True 时需要设置，且该项目指定为 `9101`
    
    * `ws_conn_url`: websocket链接地址
    
    * `mobile_cookie`: 手机端cookie，是pt_key开头的那个
    
    * `users`: web端cookie，通过add_cookie.py添加


5.  添加`cookie`

    * web端cookie：请在项目目录下执行`python3 add_cookie.py`， 在打开的浏览器界面登录你的京东，此时你可以看到`config.json`已经有了你的用户信息（**请不要随意泄露你的cookie**）
      
    * 手机端cookie：在 `config.json` 中写入 `mobile_cookie` 项，注意是pt_key开头的那个（**请不要随意泄露你的cookie**）

6.  执行主程序

    在项目目录下执行`python3 main.py`，等待执行完毕即可

## ScreenShots

![测试图1](https://github.com/yqchilde/JDMemberCloseAccount/blob/main/screenshots/test_img1.gif)

![测试图2](https://github.com/yqchilde/JDMemberCloseAccount/blob/main/screenshots/test_img2.gif)

# Thanks

感谢以下作者开源JD相关项目供我学习使用

[@AntonVanke](https://github.com/AntonVanke/JDBrandMember)

