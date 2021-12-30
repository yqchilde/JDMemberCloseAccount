# -*- coding: utf-8 -*
'''
cron: 15 2 * * * wskey.py
new Env('wskey转换');
'''
import threading
import os
import platform
import time
from utils.config import get_config
from utils.wskToCk import getToken
from main import JDMemberCloseAccount

sys_type = ""


def changeConfigFileByKey(ck, port):
    with open("./config.yaml", "r", encoding='UTF-8') as f:

        res_str = ''
        for line in f.readlines():
            if 'cookie:' in line:
                line = 'cookie: "' + ck + '"\n'
            if 'smsport' in line:
                line = line.split(':')[0] + ': ' + str(port) + '\n'
            res_str += line

    f = open("./config.yaml", "w", encoding='UTF-8')
    f.write(res_str)
    f.close()


def runMain():
    """
    根据不同平台运行退会主程序
    windows采用分窗口独立运行
    其他系统采用直接运行
    :return:
    """
    if (sys_type == 'Windows'):
        res = os.popen("python --version")
        res = res.read()
        f = open("./runmain.bat", "w", encoding='UTF-8')
        if 'python 3'.upper() in res.upper():
            f.write('start /wait cmd /C python ' + 'main.py')
        else:
            f.write('start /wait cmd /C python3 ' + 'main.py')
        f.close()
        os.system('runmain.bat')
    else:
        if (sys_type == 'Linux'):
            JDMemberCloseAccount().main()
        else:
            JDMemberCloseAccount().main()


def runByPort(keylist, port):
    """
    根据端口运行主代码
    :param keylist:
    :param port:
    :return:
    """
    keys = keylist.split("&")
    for key in keys:
        pin = key.split(";")[0]
        if "wskey" in key:
            print("转化wskey:" + pin + "\n")
            return_ws = getToken(key)
            if return_ws[0]:
                key = return_ws[1]
            else:
                print("wskey转cookie失败")
        else:
            if "pt_key" not in key:
                return
        changeConfigFileByKey(key, port)
        runMain()


def runcmdlinux(cmd):
    """
    linux下运行指令
    :param cmd:
    :return:
    """
    import subprocess
    user_str = subprocess.getoutput(cmd)
    user_list = user_str.splitlines()  # 列表形式分隔文件内容(默认按行分隔)
    for i in user_list:
        u_info = i.split(':')
        print("username is {} uid is ".format(u_info[0], u_info[2]))


def close_process(process_name):
    """
    windows端关闭制定进程
    :param process_name:
    :return:
    """
    if process_name[-4:].lower() != ".exe":
        process_name += ".exe"
    os.system("taskkill /f /im " + process_name)


def closeAllChrome():
    """
    关闭所有chrome浏览器
    :return:
    """

    if sys_type == 'Windows':
        close_process("chrome.exe")
    else:
        if sys_type == 'Linux':
            runcmdlinux("mykill chrome")
        else:
            print('其他')


def Multi_Close():
    multi_enable = get_config()["multi"]["multi_enable"]

    if not multi_enable:
        JDMemberCloseAccount().main()
        return

    # 获取配置文件里的所有key和port
    key_list = []
    port_list = []
    for i in range(10):
        try:
            key_list.append(get_config()["multi"]["key" + str(i + 1)])
            port_list.append(get_config()["multi"]["port" + str(i + 1)])
        except:
            pass

    # 根据port设置创建启动进程
    thread_list = []
    for i in range(len(port_list)):
        thread_list.append(threading.Thread(target=runByPort, args=(key_list[i], port_list[i])))
        thread_list[len(thread_list) - 1].start()
        time.sleep(60)  # 根据单个端口包含的swkey数量确认延时时间，保证修改config文件时不会冲突混乱

    # 等待所有的号都退完后关闭chrome
    for i in range(len(thread_list)):
        thread_list[i].join()
    closeAllChrome()


if __name__ == '__main__':
    cookie_all = []

    sys_type = platform.system()
    closeAllChrome()
    print("\n开启自动退会功能\n")

    # 启动一次立即执行
    Multi_Close()

    # 定时自动退会相关
    if get_config()["main"]["cron_enable"]:
        cron = get_config()["main"]["cron"]
        if len(cron.split(" ")) != 5:
            print("cron.cron 定时设置错误，必须为5位")
        from apscheduler.schedulers.blocking import BlockingScheduler
        from apscheduler.triggers.cron import CronTrigger

        scheduler = BlockingScheduler(timezone='Asia/Shanghai')
        scheduler.add_job(Multi_Close, CronTrigger.from_crontab(cron))
        scheduler.start()
