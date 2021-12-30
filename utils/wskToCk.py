
import json
import requests
import logging



logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

sv = ''
st = ''
uuid = ''
sign = ''


def get_sign():
    """
    获取签名值
    返回值 svv, stt, suid, jign
    :return:
    """
    url = 'https://hellodns.coding.net/p/sign/d/jsign/git/raw/master/sign'
    res = requests.get(url=url, verify=False, timeout=20)
    sign_list = json.loads(res.text)
    svv = sign_list['sv']
    stt = sign_list['st']
    suid = sign_list['uuid']
    jign = sign_list['sign']
    return svv, stt, suid, jign


def appjmp(wskey, tokenKey):
    """
    swkey转cookie
    :param wskey:
    :param tokenKey:
    :return: bool 转换是否成功 jd_ck 成功的话，cookie值
    """
    headers = {
        'User-Agent': 'okhttp/3.12.1;jdmall;android;version/10.1.2;build/89743;screen/1440x3007;os/11;network/wifi;',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    }
    params = {
        'tokenKey': tokenKey,
        'to': 'https://plogin.m.jd.com/cgi-bin/m/thirdapp_auth_page?token=AAEAIEijIw6wxF2s3bNKF0bmGsI8xfw6hkQT6Ui2QVP7z1Xg',
        'client_type': 'android',
        'appid': 879,
        'appup_type': 1,
    }
    url = 'https://un.m.jd.com/cgi-bin/app/appjmp'
    try:
        res = requests.get(url=url, headers=headers, params=params, verify=False, allow_redirects=False, timeout=20)
        res_set = res.cookies.get_dict()
        pt_key = 'pt_key=' + res_set['pt_key']
        pt_pin = 'pt_pin=' + res_set['pt_pin']
        jd_ck = str(pt_key) + ';' + str(pt_pin) + ';'
        wskey = wskey.split(";")[0]
        if 'fake' in pt_key:
            logger.info(str(wskey) + ";WsKey状态失效\n")
            return False, jd_ck
        else:
            logger.info(str(wskey) + ";WsKey状态正常\n")
            return True, jd_ck
    except:
        logger.info("JD接口转换失败, 默认WsKey失效\n")
        wskey = "pt_" + str(wskey.split(";")[0])
        return False, wskey


def boom():
    url = 'https://hellodns.coding.net/p/sign/d/jsign/git/raw/master/boom'
    res = requests.get(url=url, verify=False, timeout=60)
    ex = int(res.text)
    if ex != 0:
        print("Check Failure")
        print("--------------------\n")
        sys.exit(0)
    else:
        print("Verification passed")
        print("--------------------\n")


def getToken(wskey):
    boom()
    sv, st, uuid, sign = get_sign()

    headers = {'cookie': wskey,
               'User-Agent': 'okhttp/3.12.1;jdmall;android;version/10.1.2;build/89743;screen/1440x3007;os/11;network/wifi;',
               'content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'charset': 'UTF-8',
               'accept-encoding': 'br,gzip,deflate'}
    params = {'functionId': 'genToken', 'clientVersion': '10.1.2', 'client': 'android', 'uuid': uuid, 'st': st,
              'sign': sign, 'sv': sv}
    url = 'https://api.m.jd.com/client.action'
    data = 'body=%7B%22action%22%3A%22to%22%2C%22to%22%3A%22https%253A%252F%252Fplogin.m.jd.com%252Fcgi-bin%252Fm%252Fthirdapp_auth_page%253Ftoken%253DAAEAIEijIw6wxF2s3bNKF0bmGsI8xfw6hkQT6Ui2QVP7z1Xg%2526client_type%253Dandroid%2526appid%253D879%2526appup_type%253D1%22%7D&'
    res = requests.post(url=url, params=params, headers=headers, data=data, verify=False)
    res_json = json.loads(res.text)
    tokenKey = res_json['tokenKey']
    return appjmp(wskey, tokenKey)


def appjmp(wskey, tokenKey):

    headers = {
        'User-Agent': 'okhttp/3.12.1;jdmall;android;version/10.1.2;build/89743;screen/1440x3007;os/11;network/wifi;',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3', }
    params = {'tokenKey': tokenKey,
              'to': 'https://plogin.m.jd.com/cgi-bin/m/thirdapp_auth_page?token=AAEAIEijIw6wxF2s3bNKF0bmGsI8xfw6hkQT6Ui2QVP7z1Xg',
              'client_type': 'android', 'appid': 879, 'appup_type': 1, }
    url = 'https://un.m.jd.com/cgi-bin/app/appjmp'
    res = requests.get(url=url, headers=headers, params=params, verify=False, allow_redirects=False)
    res_set = res.cookies.get_dict()
    pt_key = 'pt_key=' + res_set['pt_key']
    pt_pin = 'pt_pin=' + res_set['pt_pin']
    jd_ck = str(pt_key) + ';' + str(pt_pin) + ';'
    wskey = wskey.split(";")[0]
    if 'fake' in pt_key:
        print(wskey, "wskey状态失效\n")
        return False, jd_ck
    else:
        print(wskey, "wskey状态正常\n")
        return True, jd_ck
