import requests
from hashlib import md5


class ChaoJiYing(object):
    """
    超级鹰验证类
    超级鹰打码地址：https://www.chaojiying.com
    """

    def __init__(self, _config):
        self.username = _config["cjy_username"]
        self.password = md5(_config["cjy_password"].encode('utf-8')).hexdigest()
        self.soft_id = _config["cjy_soft_id"]
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def post_pic(self, im, code_type):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {'codetype': code_type}
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files,
                          headers=self.headers)
        return r.json()

    def report_error(self, im_id):
        """im_id: 报错题目的图片 ID"""
        params = {'id': im_id}
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()
