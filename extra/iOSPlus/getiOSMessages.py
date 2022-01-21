#!/bin/env python3
# -*- coding: utf-8 -*
'''
项目名称: JDMemberCloseAccount / getiOSMessages
Author: Curtin
功能：
Date: 2021/6/12 上午9:20
'''
##### 设置jd_wstool的ip地址
ipaddr = '192.168.0.101'
## 刷新时间（秒）
sleepTIme = 3
#iOS14.3测试正常
smsdb='/private/var/mobile/Library/SMS/sms.db'
#####

import sys
import sqlite3
from requests import get
import time, datetime
import re

#####################
receiveRowid = 0
receiveTime = 0
aginNUm = 0
def printT(s):
        print("[{0}]: {1}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), s))

if sys.platform != 'ios':
    print("sorry，仅支持ios且越狱的设备~")
    exit(0)
try:
    conn = sqlite3.connect(smsdb)
    curs = conn.cursor()
    result = curs.execute("SELECT rowid,date FROM message order by date desc limit 1")
    for i in result:
        receiveRowid = i[0]
        receiveTime = i[1]
except Exception as e:
    print("sorry，仅支持ios且越狱的设备~\n")
    exit(2)

#正则获取验证码
def getCode(text):
    re.compile(r'')
    r = re.compile(r'.*?(\d{6}).*?')
    r = r.findall(text)
    if len(r) > 0:
        return r[0]
    else:
        return 0
#提交验证码
def postCode(code):
    global aginNUm
    headers = {
        "Content-Type": 'text/html',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    try:
        get(url=f'http://{ipaddr}:5201/publish?smsCode={code}', headers=headers)
        #print(resp.json())
    except:
        aginNUm += 1
        if aginNUm < 2:
            return postCode(code)
        else:
            print("请检查提交的ip地址是否正确，是否防火墙拦截？")
            exit(1)

#获取最新验证码短信
def getMessages():
    global receiveTime, receiveRowid
    sql = '''SELECT rowid,text,date FROM message where text like \'%京东%验证码%\'  order by date desc limit 1'''
    result = curs.execute(sql)
    if len(list(result)) > 0:
        for i in curs.execute(sql):
            getTowid = i[0]
            getText = i[1]
            getTime = i[2]
            if getTowid > receiveRowid and getTime > receiveTime:
                receiveRowid = getTowid
                receiveTime = getTime
                code = getCode(getText)
                printT(f"收到最新验证码: {code}")
                if code:
                    postCode(code)

def run():
    print("启动ios端验证码监听...")
    while True:
        getMessages()
        time.sleep(sleepTIme)

if __name__ == '__main__':
    run()

