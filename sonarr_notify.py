import json
import os
import re

import requests

# 企业微信应用的配置，仅需前4项，若第五项配置了仅在缓存图片未找到的情况下使用;配置参考http://note.youdao.com/s/HMiudGkb
QYWX_AM = ''
# 此为SONARR 里的缓存图片路径，找一下MediaCover 这个目录的位置即可，因为套件版目录和docker会不一样。暂时没想到什么方法自动获取。所以就手动配置下
SONARR_PATH = '/volume2/@appstore/nzbdrone/var/.config/Sonarr/MediaCover/'
# 前往 https://sm.ms/ 注册帐号后填入 SMMS_ID 为用户名，SMMS_PSWD为密码， 免费空间5G
SMMS_ID = ''
SMMS_PSWD = ''
# 推送的图片质量 1表示高质量, 2表示低质量。 高质量大概一张100KB， 低质量一张大概30KB。根据自己情况修改
PHOTO_QUALITY = 1


# 企业微信 APP 推送
def wecom_app(title, content, media_url=''):
    try:
        if not QYWX_AM:
            print("QYWX_AM 并未设置！！\n取消推送")
            return
        QYWX_AM_AY = re.split(',', QYWX_AM)
        if 4 < len(QYWX_AM_AY) > 5:
            print("QYWX_AM 设置错误！！\n取消推送")
            return
        corpid = QYWX_AM_AY[0]
        corpsecret = QYWX_AM_AY[1]
        touser = QYWX_AM_AY[2]
        agentid = QYWX_AM_AY[3]
        try:
            media_id = QYWX_AM_AY[4]
        except:
            media_id = ''
        wx = WeCom(corpid, corpsecret, agentid)
        # 如果没有配置 media_id 默认就以 text 方式发送
        if media_url:
            response = wx.send_news(title, content, media_url, touser)
        elif not media_id:
            message = title + '\n\n' + content
            response = wx.send_text(message, touser)
        else:
            response = wx.send_mpnews(title, content, media_id, touser)
        if response == 'ok':
            print('推送成功！')
        else:
            print('推送失败！错误信息如下：\n', response)
    except Exception as e:
        print(e)


class WeCom:
    def __init__(self, corpid, corpsecret, agentid):
        self.CORPID = corpid
        self.CORPSECRET = corpsecret
        self.AGENTID = agentid

    def get_access_token(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        values = {'corpid': self.CORPID,
                  'corpsecret': self.CORPSECRET,
                  }
        req = requests.post(url, params=values)
        data = json.loads(req.text)
        return data["access_token"]

    def send_text(self, message, touser="@all"):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.get_access_token()
        send_values = {
            "touser": touser,
            "msgtype": "text",
            "agentid": self.AGENTID,
            "text": {
                "content": message
            },
            "safe": "0"
        }
        send_msges = (bytes(json.dumps(send_values), 'utf-8'))
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]

    def send_mpnews(self, title, message, media_id, touser="@all"):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.get_access_token()
        send_values = {
            "touser": touser,
            "msgtype": "mpnews",
            "agentid": self.AGENTID,
            "mpnews": {
                "articles": [
                    {
                        "title": title,
                        "thumb_media_id": media_id,
                        "author": "Author",
                        "content_source_url": "",
                        "content": message.replace('\n', '<br/>'),
                        "digest": message
                    }
                ]
            }
        }
        send_msges = (bytes(json.dumps(send_values), 'utf-8'))
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]

    def send_news(self, title, message, meida_url, touser="@all"):
        print(meida_url)
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.get_access_token()
        send_values = {
            "touser": touser,
            "msgtype": "news",
            "agentid": self.AGENTID,
            "news": {
                "articles": [
                    {
                        "title": title,
                        "picurl": meida_url,
                        "author": "Author",
                        "description": message
                    }
                ]
            }
        }
        send_msges = (bytes(json.dumps(send_values), 'utf-8'))
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]


class Smms:

    @classmethod
    def get_token(cls, username, password):
        """
        提供用户名和密码返回用户的 API Token，若用户没有生成 Token 则会自动为其生成一个。
        :param username: 用户名/邮件地址
        :param password: 密码
        :return: API Token
        """
        url = 'https://sm.ms/api/v2/token'
        data = {'username': username, 'password': password}
        re = requests.post(url, data=data)

        if json.loads(re.content)['success']:
            token = json.loads(re.content)['data']['token']
            return token
        else:
            raise KeyError

    @classmethod
    def upload(cls, image, token=None):
        """
        图片上传接口。
        :param image: 图片的地址
        :param token: API Token
        :return: 返回图片上传后的URL
        """
        url = 'https://sm.ms/api/v2/upload'
        params = {'format': 'json', 'ssl': True}
        files = {'smfile': open(image, 'rb')}
        headers = {'Authorization': token}
        if token:
            re = requests.post(url, headers=headers, files=files, params=params)
        else:
            re = requests.post(url, files=files, params=params)
        re_json = json.loads(re.text)
        try:
            if re_json['success']:
                return re_json['data']['url']
            else:
                return re_json['images']
        except KeyError:
            if re_json['code'] == 'unauthorized':
                # raise ConnectionRefusedError
                return None
            if re_json['code'] == 'flood':
                # raise ConnectionAbortedError
                return None

    @classmethod
    def get_history(cls, token):
        """
        提供 API Token，获得对应用户的所有上传图片信息。
        :param token: API Token
        :return: {dict}
        """
        url = 'https://sm.ms/api/v2/upload_history'
        params = {'format': 'json', 'ssl': True}
        headers = {'Authorization': token}
        re = requests.get(url, headers=headers, params=params)
        re_json = json.loads(re.text)
        try:
            if re_json['success']:
                return re_json['data']
            else:
                # raise KeyError
                return None
        except KeyError:
            if re_json['code'] == 'unauthorized':
                # raise ConnectionRefusedError
                return None

    @classmethod
    def get_history_ip(cls):
        """
        获得上传历史. 返回同一 IP 一个小时内上传的图片数据。
        :return: {dict}
        """
        url = 'https://sm.ms/api/v2/history'
        params = {'format': 'json', 'ssl': True}
        re = requests.get(url, params=params)
        re_json = json.loads(re.text)
        if re_json['success']:
            return re_json['data']
        else:
            # raise KeyError
            return None


class Smms:

    @classmethod
    def get_token(cls, username, password):
        """
        提供用户名和密码返回用户的 API Token，若用户没有生成 Token 则会自动为其生成一个。
        :param username: 用户名/邮件地址
        :param password: 密码
        :return: API Token
        """
        url = 'https://sm.ms/api/v2/token'
        data = {'username': username, 'password': password}
        re = requests.post(url, data=data)

        if json.loads(re.content)['success']:
            token = json.loads(re.content)['data']['token']
            return token
        else:
            raise KeyError

    @classmethod
    def upload(cls, image, token=None):
        """
        图片上传接口。
        :param image: 图片的地址
        :param token: API Token
        :return: 返回图片上传后的URL
        """
        url = 'https://sm.ms/api/v2/upload'
        params = {'format': 'json', 'ssl': True}
        files = {'smfile': open(image, 'rb')}
        headers = {'Authorization': token}
        if token:
            re = requests.post(url, headers=headers, files=files, params=params)
        else:
            re = requests.post(url, files=files, params=params)
        re_json = json.loads(re.text)
        print(re_json)
        try:
            if re_json['success']:
                return re_json['data']['url']
            else:
                return re_json['images']
        except KeyError:
            if re_json['code'] == 'unauthorized':
                # raise ConnectionRefusedError
                return None
            if re_json['code'] == 'flood':
                # raise ConnectionAbortedError
                return None

    @classmethod
    def get_history(cls, token):
        """
        提供 API Token，获得对应用户的所有上传图片信息。
        :param token: API Token
        :return: {dict}
        """
        url = 'https://sm.ms/api/v2/upload_history'
        params = {'format': 'json', 'ssl': True}
        headers = {'Authorization': token}
        re = requests.get(url, headers=headers, params=params)
        re_json = json.loads(re.text)
        try:
            if re_json['success']:
                return re_json['data']
            else:
                # raise KeyError
                return None
        except KeyError:
            if re_json['code'] == 'unauthorized':
                # raise ConnectionRefusedError
                return None

    @classmethod
    def get_history_ip(cls):
        """
        获得上传历史. 返回同一 IP 一个小时内上传的图片数据。
        :return: {dict}
        """
        url = 'https://sm.ms/api/v2/history'
        params = {'format': 'json', 'ssl': True}
        re = requests.get(url, params=params)
        re_json = json.loads(re.text)
        if re_json['success']:
            return re_json['data']
        else:
            # raise KeyError
            return None


def get_env_value(key):
    if key in os.environ and os.environ[key]:
        return os.environ[key]
    else:
        return None


def HRS(size):
    units = ('B', 'KB', 'MB', 'GB', 'TB', 'PB')
    for i in range(len(units) - 1, -1, -1):
        if size >= 2 * (1024 ** i):
            return '%.2f' % (size / (1024 ** i)) + ' ' + units[i]


def get_file_url(series_id):
    dir_path = SONARR_PATH + series_id
    if os.path.exists(dir_path):
        photo_name = 'fanart-180.jpg'
        if PHOTO_QUALITY == 1:
            photo_name = 'fanart-360.jpg'
        elif PHOTO_QUALITY == 2:
            photo_name = 'fanart-180.jpg'

        if os.path.exists(os.path.join(dir_path, photo_name)):
            media_file = os.path.join(dir_path, photo_name)
            token = Smms.get_token(SMMS_ID, SMMS_PSWD)
            url = Smms.upload(media_file, token)
            return url
    return None


def grab():
    detail = {
        'id': os.environ.get('sonarr_series_id', None),
        'title': os.environ.get('sonarr_series_title', None),
        'imdbid': os.environ.get('sonarr_series_imdbid', None),
        'tvdbid': os.environ.get('sonarr_series_tvdbid', None),
        'quality': os.environ.get('sonarr_release_quality', None),
        'size': os.environ.get('sonarr_release_size', None),
        'episodecount': os.environ.get('sonarr_release_episodecount', None),
        'episodenumbers': os.environ.get('sonarr_release_episodenumbers', None),
        'seasonnumber': os.environ.get('sonarr_release_seasonnumber', None),
        'torrent_title': os.environ.get('sonarr_release_title', None),
        'indexer': os.environ.get('sonarr_release_indexer', None),
    }
    msg = '开始下载\n剧名：' + detail['title']
    url = ''
    if detail['seasonnumber']:
        msg = msg + ' S' + detail['seasonnumber'].zfill(2)
    if detail['episodenumbers']:
        msg = msg + 'E' + detail['episodenumbers'].zfill(2)
    if detail['quality']:
        msg += '\n视频质量：' + detail['quality']
    if detail['size']:
        msg += '\n视频大小：' + HRS(int(detail['size']))
    if detail['indexer']:
        msg += '\n抓取自：  ' + detail['indexer']
    if detail['id']:
        url = get_file_url(detail['id'])
    if not url:
        wecom_app('Sonarr抓取通知', msg)
    else:
        wecom_app('Sonarr抓取通知', msg, url)

    print("Grab")


def download():
    detail = {
        'id': os.environ.get('sonarr_series_id', None),
        'title': os.environ.get('sonarr_series_title', None),
        'episodenumbers': os.environ.get('sonarr_episodefile_episodenumbers', None),
        'seasonnumber': os.environ.get('sonarr_episodefile_seasonnumber', None),
        'quality': os.environ.get('sonarr_episodefile_quality', None),
        'isupgrade': os.environ.get('sonarr_isupgrade', None),
    }

    msg = '下载完成\n剧名：' + detail['title']
    url = ''
    if detail['seasonnumber']:
        msg = msg + ' S' + detail['seasonnumber'].zfill(2)
    if detail['episodenumbers']:
        msg = msg + 'E' + detail['episodenumbers'].zfill(2)
    if detail['quality']:
        msg += '\n视频质量：' + detail['quality']
    #if detail['isupgrade']:
    #    msg += '\n格式升级：' + '是' if bool(detail['isupgrade']) else '否'

    if detail['id']:
        url = get_file_url(detail['id'])
    if not url:
        wecom_app('Sonarr下载通知', msg)
    else:
        wecom_app('Sonarr下载通知', msg, url)

    print("Download")


def rename():
    # detail = {
    #     'id': os.environ.get('sonarr_series_id', None),
    #     'title': os.environ.get('sonarr_series_title', None),
    #     'episodenumbers': os.environ.get('sonarr_episodefile_episodenumbers', None),
    #     'seasonnumber': os.environ.get('sonarr_episodefile_seasonnumber', None),
    #     'quality': os.environ.get('sonarr_episodefile_quality', None),
    # }

    print("Rename")


def episode_deleted():
    detail = {
        'id': os.environ.get('sonarr_series_id', None),
        'title': os.environ.get('sonarr_series_title', None),
        'episodenumbers': os.environ.get('sonarr_episodefile_episodenumbers', None),
        'seasonnumber': os.environ.get('sonarr_episodefile_seasonnumber', None),
        'quality': os.environ.get('sonarr_episodefile_quality', None),
        'path': os.environ.get('sonarr_episodefile_path', None),
    }
    msg = '文件已删除\n剧名：' + detail['title']
    url = ''
    if detail['seasonnumber']:
        msg = msg + ' S' + detail['seasonnumber'].zfill(2)
    if detail['episodenumbers']:
        msg = msg + 'E' + detail['episodenumbers'].zfill(2)
    if detail['quality']:
        msg += '\n视频质量：' + detail['quality']
    if detail['path']:
        msg += '\n文件路径：' + detail['path']
    if detail['id']:
        url = get_file_url(detail['id'])
    if not url:
        wecom_app('Sonarr删除通知', msg)
    else:
        wecom_app('Sonarr删除通知', msg, url)
    print("EpisodeDeleted")


def series_deleted():
    detail = {
        'id': os.environ.get('sonarr_series_id', None),
        'title': os.environ.get('sonarr_series_title', None),
        'path': os.environ.get('sonarr_series_path', None),
        'deletedfiles': os.environ.get('sonarr_series_deletedfiles', None),  # True or False
    }
    msg = '剧集已删除\n剧名：' + detail['title']
    url = ''
    if detail['path']:
        msg += '\n路径：' + detail['path']
    if detail['deletedfiles']:
        msg += '\n删除文件：' + '是' if bool(detail['deletedfiles']) else '否'
    if detail['id']:
        url = get_file_url(detail['id'])
    if not url:
        wecom_app('Sonarr删除通知', msg)
    else:
        wecom_app('Sonarr删除通知', msg, url)
    print("SeriesDeleted")


def health_issue():
    detail = {
        'level': os.environ.get('sonarr_health_issue_level', None),  # Ok, Notice, Warning, or Error
        'message': os.environ.get('sonarr_health_issue_message', None),
        'type': os.environ.get('sonarr_health_issue_type', None),
        'wiki': os.environ.get('sonarr_health_issue_wiki', None),
    }
    msg = ''
    if detail['level']:
        level = detail['level']
        if level == 'Ok':
            msg += '一切正常！Perfect！'
        elif level == 'Notice':
            msg += '建议：'
        elif level == 'Warning':
            msg += '警告：'
        elif level == 'Error':
            msg += '错误：'
    if detail['message']:
        msg += '\n' + detail['message']
    wecom_app('Sonarr状态通知', msg)
    print("HealthIssue")


def default():
    print("Default")


def test():
    wecom_app('测试', "Sonarr 测试数据")


type_dict = {
    "Grab": grab,
    "Download": download,
    "Rename": rename,
    "EpisodeDeleted": episode_deleted,
    "SeriesDeleted": series_deleted,
    "HealthIssue": health_issue,
    "Test": test
}

if __name__ == '__main__':
    if "sonarr_eventtype" in os.environ and os.environ["sonarr_eventtype"]:
        event_type = os.environ["sonarr_eventtype"]
        event_fun = type_dict.get(event_type, default)
        event_fun()
    else:
        wecom_app('Sonarr', "未检测到参数，")
