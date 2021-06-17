# JDMemberCloseAccount

## Describe

该分支仅用于从`main`分支拉取最新代码并利用`pyinstall`进行打包，不会将其合并至`main`

了解其他详细配置请浏览 [配置说明](https://github.com/yqchilde/JDMemberCloseAccount/blob/main/README.md)

## Run

1. 打包好的项目如何运行呢？

    * **前提：** 在运行之前请确保目录下的`drivers`目录里有你的驱动，`config.yaml`配置完善

    * macOS(amd64)：从终端中进入项目，然后 `./main` 即可运行并产生日志
    
    * win：

## Build

以下是构建时的操作，非自己有打包需求的用户不用关心

### Step

1.  首先配置好环境

    建议使用虚拟环境，避免其它的包造成影响

    ```shell
    pip3 install -r requirements.txt
    ```

2.  安装 Pyinstaller

    ```shell
    pip3 install pyinstaller
    ```

3.  使用虚拟环境的 Pyinstaller 打包

    >   在打包之前，你还需要确认你的文件夹下是否有`conv-lite-fc`，它是模型集。如果没有的话，可能会导致打包失败。运行一下`captcha/cn_ocr.py`就会自动下载。

    #### mac

    ```shell
    pyinstaller -F -y main.py --add-data="./conv-lite-fc:./conv-lite-fc"
    ```

    ```shell
    # 同样你可以打包 MAC APP 但你必须解决好`config.yaml`和浏览器驱动问题
    pyinstaller --onedir -y -w main.py --add-data="./conv-lite-fc:./conv-lite-fc" --icon=logo.icns
    ```

    #### win

    ```shell
    pyinstaller -F -y main.py --add-data="./conv-lite-fc:./conv-lite-fc" --icon=logo.ico
    ```

### Question

1.  运行时出现`MxNET`报错怎么办？

    >   在`venv/lib/python3.*/site-packages/PyInstaller/hooks`下创建一个`MxNET`钩子：
    >
    >   创建`hook-mxnet.py`
    >
    >   >   ```python
    >   >   from PyInstaller.utils.hooks import get_package_paths
    >   >   
    >   >   datas = [(get_package_paths('mxnet')[1], "mxnet"), ]
    >   >   ```

2.  打包的文件过大怎么办？

    >   你应该运行`venv::pyinstaller`而不是基础环境下的`pyinstaller`
    
3.  一直打包不成功怎么办？

    >   [@jdMemberCloseAccount ](https://t.me/jdMemberCloseAccount)电报群

4.  打包还需要遵循哪些问题？

    >   1.  打包的程序不应带有病毒破坏性程序
    >   2.  打包的程序不得收集用户信息(包括但不限于`Cookie`)和除改善程序为目的的数据收集

### Copy file

复制以下文件夹到`dist`目录

>   drivers/
>
>   config.yaml
>
>   LISCENSE
>
>   extra  
> 
>   README.md

