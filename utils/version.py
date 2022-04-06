import datetime
import requests


def check_version(logger):
    # noinspection PyBroadException
    try:
        url = "https://gitee.com/yqchilde/JDMemberCloseAccount/raw/main/utils/version"
        resp = requests.get(url)
        if resp.status_code == 404:
            return
        elif resp.status_code == 200:
            with open('./utils/version', 'r') as f:
                local_version = f.read()
                remote_version = resp.text.strip()
            if local_version != remote_version:
                gitee_api = "https://gitee.com/api/v5/repos/yqchilde/JDMemberCloseAccount/commits?per_page=1"
                resp = requests.get(gitee_api).json()
                updated = resp[0]["commit"]["committer"]["date"]
                updated = datetime.datetime.strptime(updated, "%Y-%m-%dT%H:%M:%S+00:00")
                updated = updated + datetime.timedelta(hours=8)
                logger.info(
                    "检测到项目代码有更新，最近一次更新时间为 [%s]，为了保证项目可用性，希望您尽可能的使用最新版！" % updated
                )

    except Exception:
        pass
