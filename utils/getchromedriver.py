import os
import subprocess
import zipfile
import winreg
import re
import requests
import logging


chromedriverpath = ''


def excuteCommand(com):
    ex = subprocess.Popen(com, stdout=subprocess.PIPE, shell=True)
    out, err = ex.communicate()
    status = ex.wait()
    print("cmd in:", com)
    print("cmd out: ", out.decode())
    return out.decode()

def download(link, file_name):
    response = requests.get(link)
    file = response.content
    with open(file_name, 'wb') as f:
        f.write(file)


def unzip(zip_file, filepath):
    extracting = zipfile.ZipFile(zip_file)
    extracting.extractall(filepath)
    extracting.close()
    os.remove(zip_file)


def re_all(rule, body):
    rule_all = re.findall(re.compile(r'%s' % (rule)), body)
    if len(rule_all) > 0:
        return rule_all
    else:
        return False


def get_chromedriver_list():
    '''获取驱动列表'''
    url = 'http://npm.taobao.org/mirrors/chromedriver/'
    r = requests.get(url).text
    return re_all(r'/mirrors/chromedriver/([0-9]+\.[0-9]+.[0-9]+.[0-9]+)/', r)


def get_chromedriver(version):
    global chromedriverpath
    '''下载驱动'''
    link = 'http://npm.taobao.org/mirrors/chromedriver/%s/chromedriver_win32.zip' % version
    if os.path.exists(chromedriverpath):
        os.remove(chromedriverpath)
    download(link, chromedriverpath + '.zip')
    outdir = os.path.dirname(chromedriverpath)
    unzip(chromedriverpath + '.zip', outdir)
    return True


def get_chrome_version():
    key = False
    if not key:
        # 64位
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome")
        except:
            pass
    if not key:
        # 32位
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome")
        except:
            pass
    if not key:
        return False
    version = winreg.QueryValueEx(key, "version")[0]
    return version


def get_driver_version():
    global chromedriverpath
    info = excuteCommand(chromedriverpath + ' --version')
    if info:
        return info.split(' ')[1]
    return False


def check_driver_version(driverpath):
    global chromedriverpath
    chromedriverpath = driverpath
    print('获取 chromedriver 版本')
    if not os.path.exists(chromedriverpath):
        print('没有找到 chromedriver.exe')
        driver_version = '无'
    else:
        driver_version = get_driver_version()
        driver_version = driver_version[:driver_version.rfind(".")]
    chrome_version = get_chrome_version()
    if not chrome_version:
        print('没有按照chrome')
        return False
    chrome_version = chrome_version[:chrome_version.rfind(".")]
    if driver_version != chrome_version:
        print('浏览器(%s)和驱动版本(%s)不匹配' % (chrome_version, driver_version))
        version_list = get_chromedriver_list()
        if not version_list:
            print('获取驱动列表失败')
            return False
        for version in version_list:
            if chrome_version in version:
                if not get_chromedriver(version):
                    print('下载驱动失败')
                    return False
                else:
                    print('驱动更新成功')
                    return True
        print('没有找到对应的驱动版本')
        return False
    else:
        print('版本匹配通过')
        return True