import json
import os
import re

import requests
import yaml

# 请在 config.yml 文件中配置
QYWX = ''
SMMS_ID = ''
SMMS_PSWD = ''
PHOTO_QUALITY = 1
SONARR_PATH = ''
RADARR_PATH = ''


# 企业微信 APP 推送
def wecom_app(title, content, media_url=''):
    try:
        if not QYWX:
            print("QYWX_AM 并未设置！！\n取消推送")
            return
        QYWX_AM_AY = re.split(',', QYWX)
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


def load_user_config():
    global QYWX
    global SMMS_ID
    global SMMS_PSWD
    global PHOTO_QUALITY
    global SONARR_PATH
    global RADARR_PATH
    user_setting_filepath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.yml')
    if os.path.exists(user_setting_filepath):
        with open(user_setting_filepath, 'r', encoding='utf-8') as file:
            user_config = yaml.safe_load(file)
        QYWX = user_config['user']['qywx']
        if not QYWX:
            raise KeyError('未配置企业微信')
        SMMS_ID = user_config['user']['smms_id']
        SMMS_PSWD = user_config['user']['smms_pswd']
        PHOTO_QUALITY = user_config['user']['photo_quality']
        SONARR_PATH = user_config['sonarr']['sonarr_path']
        RADARR_PATH = user_config['radarr']['radarr_path']


def get_info_from_imdb_id(imdb_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                      '537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }
    api_url = "https://movie.douban.com/j/subject_suggest?q="
    req_url = api_url + imdb_id
    try:
        return requests.get(req_url, headers=headers).json()[0]
    except Exception:
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


def get_file_url(series_id, arr_type):
    if not series_id:
        return None
    dir_path = os.path.join(os.environ["HOME"], '.config', arr_type, 'MediaCover', series_id)
    if arr_type == 'Sonarr':
        if SONARR_PATH:
            dir_path = os.path.join(SONARR_PATH, series_id)
    elif arr_type == 'Radarr':
        if RADARR_PATH:
            dir_path = os.path.join(RADARR_PATH, series_id)

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


def fill_msg_from_detail(detail):
    title = ''
    msg = ''
    if detail.get('imdbid'):
        info = get_info_from_imdb_id(detail['imdbid'])
        if info and info.get('title'):
            detail['title'] = re.sub(r' 第\S{1,3}季', '', info['title'], count=1)
    if detail.get('title'):
        title = detail['title']
        if detail.get('seasonnumber'):
            title += ' S' + detail['seasonnumber'].zfill(2)
        if detail.get('episodenumbers'):
            title += 'E' + detail['episodenumbers'].zfill(2)
    if detail.get('quality'):
        msg += '视频质量：' + detail['quality']
    if detail.get('size'):
        msg += '\n视频大小：' + HRS(int(detail['size']))
    if detail.get('path'):
        msg += '\n文件路径：' + detail['path']
    if detail.get('isupgrade'):
        msg += '\n格式升级：' + ('是' if 'True' == detail['isupgrade'] else '否')
    if detail.get('deletedfiles'):
        msg += '\n删除文件：' + ('是' if 'True' == detail['deletedfiles'] else '否')
    if detail.get('indexer'):
        msg += '\n抓取自：' + detail['indexer']
    return title, msg


class Sonarr:
    def __init__(self):
        self.type = 'Sonarr'
        self.type_dict = {
            "Grab": self.grab,
            "Download": self.download,
            "Rename": self.rename,
            "EpisodeDeleted": self.episode_deleted,
            "SeriesDeleted": self.series_deleted,
            "HealthIssue": self.health_issue,
            "Test": self.test
        }

    def grab(self):
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
        title, msg = fill_msg_from_detail(detail)
        url = get_file_url(detail['id'], self.type)
        wecom_app('开始下载：' + title, msg, url)
        print("Grab")

    def download(self):
        detail = {
            'id': os.environ.get('sonarr_series_id', None),
            'title': os.environ.get('sonarr_series_title', None),
            'imdbid': os.environ.get('sonarr_series_imdbid', None),
            'episodenumbers': os.environ.get('sonarr_episodefile_episodenumbers', None),
            'seasonnumber': os.environ.get('sonarr_episodefile_seasonnumber', None),
            'quality': os.environ.get('sonarr_episodefile_quality', None),
            'isupgrade': os.environ.get('sonarr_isupgrade', None),
        }
        title, msg = fill_msg_from_detail(detail)
        url = get_file_url(detail['id'], self.type)
        wecom_app('下载完成：' + title, msg, url)
        print("Download")

    def rename(self):
        # detail = {
        #     'id': os.environ.get('sonarr_series_id', None),
        #     'title': os.environ.get('sonarr_series_title', None),
        #     'episodenumbers': os.environ.get('sonarr_episodefile_episodenumbers', None),
        #     'seasonnumber': os.environ.get('sonarr_episodefile_seasonnumber', None),
        #     'quality': os.environ.get('sonarr_episodefile_quality', None),
        # }

        print("Rename")

    def episode_deleted(self):
        detail = {
            'id': os.environ.get('sonarr_series_id', None),
            'title': os.environ.get('sonarr_series_title', None),
            'imdbid': os.environ.get('sonarr_series_imdbid', None),
            'episodenumbers': os.environ.get('sonarr_episodefile_episodenumbers', None),
            'seasonnumber': os.environ.get('sonarr_episodefile_seasonnumber', None),
            'quality': os.environ.get('sonarr_episodefile_quality', None),
            'path': os.environ.get('sonarr_episodefile_path', None),
        }
        title, msg = fill_msg_from_detail(detail)
        url = get_file_url(detail['id'], self.type)
        wecom_app('文件已删除：' + title, msg, url)
        print("EpisodeDeleted")

    def series_deleted(self):
        detail = {
            'id': os.environ.get('sonarr_series_id', None),
            'title': os.environ.get('sonarr_series_title', None),
            'imdbid': os.environ.get('sonarr_series_imdbid', None),
            'path': os.environ.get('sonarr_series_path', None),
            'deletedfiles': os.environ.get('sonarr_series_deletedfiles', None),  # True or False
        }
        title, msg = fill_msg_from_detail(detail)
        url = get_file_url(detail['id'], self.type)
        wecom_app('剧集已删除：' + title, msg, url)
        print("SeriesDeleted")

    def health_issue(self):
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

    def default(self):
        print("Default")

    def test(self):
        wecom_app('测试', "Sonarr 测试数据\n" + str(os.environ))

    def exec(self, fun_name):
        radarr_fun = self.type_dict.get(fun_name, self.default())
        radarr_fun()


class Radarr:

    def __init__(self):
        self.type = 'Radarr'
        self.type_dict = {
            'Grab': self.grab,
            'Download': self.download,
            'Rename': self.rename,
            'HealthIssue': self.health_issue,
            'ApplicationUpdate': self.application_update,
            'Test': self.test
        }

    def grab(self):
        detail = {
            'id': os.environ.get('radarr_movie_id', None),
            'title': os.environ.get('radarr_movie_title', None),
            'imdbid': os.environ.get('radarr_movie_imdbid', None),
            'quality': os.environ.get('radarr_release_quality', None),
            'size': os.environ.get('radarr_release_size', None),
            'indexer': os.environ.get('radarr_release_indexer', None),
        }
        title, msg = fill_msg_from_detail(detail)
        url = get_file_url(detail['id'], self.type)
        wecom_app('开始下载：' + title, msg, url)
        print("Grab")

    def download(self):
        detail = {
            'id': os.environ.get('radarr_movie_id', None),
            'title': os.environ.get('radarr_movie_title', None),
            'imdbid': os.environ.get('radarr_movie_imdbid', None),
            'quality': os.environ.get('radarr_moviefile_quality', None),
        }
        title, msg = fill_msg_from_detail(detail)
        url = get_file_url(detail['id'], self.type)
        wecom_app('下载完成：' + title, msg, url)

        print("Download")

    def rename(self):
        print("Rename")

    def application_update(self):
        print("ApplicationUpdate")

    def health_issue(self):
        print("HealthIssue")

    def default(self):
        print("Default")

    def test(self):
        wecom_app('Radarr测试', "Radarr 测试数据\n" + str(os.environ))

    def exec(self, fun_name):
        radarr_fun = self.type_dict.get(fun_name, self.default())
        radarr_fun()


if __name__ == '__main__':
    load_user_config()
    if "sonarr_eventtype" in os.environ and os.environ["sonarr_eventtype"]:
        event_type = os.environ["sonarr_eventtype"]
        Sonarr().exec(event_type)
    elif "radarr_eventtype" in os.environ and os.environ["radarr_eventtype"]:
        event_type = os.environ["radarr_eventtype"]
        Radarr().exec(event_type)
    else:
        wecom_app('XarrNotify', "未检测到参数.")
