import base64
import json
import os.path
import re
import sys
import time
from enum import Enum
from types import SimpleNamespace

import requests.models
from dateutil import parser

import log
from app.conf import ModuleConf
from app.downloader.client._base import _IDownloadClient
from app.utils import RequestUtils, StringUtils, Torrent, ExceptionUtils
from config import Config

third_party_nas_xunlei = [
    "pyjsparser",
    "Js2Py"
]
for dep in third_party_nas_xunlei:
    sys.path.append(os.path.join(Config().get_root_path(), "third_party_nas_xunlei", dep).replace("\\", "/"))
import js2py


class Downloader_NasXunlei(Enum):
    NAS_XUNLEI = "NAS 迅雷"


class NasXunlei_Status(str, Enum):
    """enum for torrent status"""

    PHASE_TYPE_PAUSED = "PHASE_TYPE_PAUSED"
    PHASE_TYPE_PENDING = "PHASE_TYPE_PENDING"
    PHASE_TYPE_RUNNING = "PHASE_TYPE_RUNNING"
    PHASE_TYPE_COMPLETE = "PHASE_TYPE_COMPLETE"
    PHASE_TYPE_ERROR = "PHASE_TYPE_ERROR"

    @property
    def stopped(self) -> bool:
        return self == "paused" or self == "complete" or self == "error"

    @property
    def download_pending(self) -> bool:
        return self == "download pending"

    @property
    def downloading(self) -> bool:
        return self == "downloading"

    def __str__(self) -> str:
        return self.value

_default_port = 5055
_nas_xunlei_icon = (
    "data:image/png;base64,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"
)
ModuleConf.DOWNLOADER_CONF["nas_xunlei"] = {
    "name": "NAS 迅雷",
    "img_url": _nas_xunlei_icon,
    "color": "#CCE0ED",
    "monitor_enable": True,
    "speedlimit_enable": True,
    "config": {
        "host": {
            "id": "nas_xunlei_host",
            "required": True,
            "title": "地址",
            "tooltip": "配置IP地址或域名，如为https则需要增加https://前缀",
            "type": "text",
            "placeholder": "127.0.0.1"
        },
        "port": {
            "id": "nas_xunlei_port",
            "required": True,
            "title": "端口",
            "type": "text",
            "placeholder": _default_port
        },
        "username": {
            "id": "nas_xunlei_username",
            "required": False,
            "title": "用户名",
            "type": "text",
            "placeholder": "admin"
        },
        "password": {
            "id": "nas_xunlei_password",
            "required": False,
            "title": "密码",
            "type": "password",
            "placeholder": "password"
        }
    }
}
ModuleConf.TORRENTREMOVER_DICT["nas_xunlei"] = {
    "name": "NAS 迅雷",
    "img_url": _nas_xunlei_icon,
    "downloader_type": Downloader_NasXunlei.NAS_XUNLEI,
    "torrent_state": {
        "PHASE_TYPE_PAUSED": "暂停",
        "PHASE_TYPE_RUNNING": "正在下载",
        "PHASE_TYPE_PENDING": "等待下载_排队",
        "PHASE_TYPE_COMPLETE": "下载完成",
        "PHASE_TYPE_ERROR": "错误",
    }
}


class NasXunlei(_IDownloadClient):
    # 下载器ID
    client_id = "nas_xunlei"
    # 下载器类型
    client_type = Downloader_NasXunlei.NAS_XUNLEI
    # 下载器名称
    client_name = Downloader_NasXunlei.NAS_XUNLEI.value

    host = None
    port = None
    username = None
    password = None
    name = "测试"
    download_dir = []

    _nxc = None

    def __init__(self, config):
        self.host = config.get('host')
        self.port = int(config.get('port')) if str(config.get('port')).isdigit() else _default_port
        self.username = config.get('username')
        self.password = config.get('password')
        self.download_dir = config.get('download_dir') or []
        self.name = config.get('name') or ""
        self.connect()


    @classmethod
    def match(cls, ctype):
        return True if ctype in [cls.client_id, cls.client_type, cls.client_name] else False

    def get_type(self):
        return self.client_type

    def connect(self):
        if self.host and self.port:
            self._nxc = self.__login_nas_xunlei()

    def __login_nas_xunlei(self):
        """
        连接 NAS 迅雷
        :return: qbittorrent对象
        """
        nxc = NasXunleiProvider(host=self.host, port=self.port, username=self.username, password=self.password)
        try:
            nxc.check_server_now()
        except Exception as e:
            log.error(f"【{self.client_name}】{self.name} 连接出错：{str(e)}")
        return nxc

    def get_status(self):
        if not self._nxc:
            return False
        try:
            self._nxc.info_watch()
            return True
        except Exception as e:
            log.error(f"【{self.client_name}】{self.name} 获取状态出错：{str(e)}")
            return False

    def get_torrents(self, ids=None, status=None, tag=None):
        """
        按条件读取种子信息
        :param ids: 种子ID，单个ID或者ID列表
        :param status: 种子状态过滤
        :param tag: 种子标签过滤
        :return: 种子信息列表，是否发生错误
        """
        if not self._nxc:
            return [], True
        try:
            all_tasks = self._nxc.get_torrents(ids=ids, status=status)
            if not all_tasks:
                return [], False
            else:
                return all_tasks, False
        except Exception as err:
            log.error(f"【{self.client_name}】{self.name} 获取种子列表出错：{str(err)}")
            ExceptionUtils.exception_traceback(err)
            return [], True

    def get_downloading_torrents(self, ids=None, tag=None):
        if not self._nxc:
            return [], True
        try:
            all_tasks = self._nxc.get_downloading_torrents(ids=ids)
            if not all_tasks:
                return None, True
            else:
                return all_tasks, False
        except Exception as err:
            log.error(f"【{self.client_name}】{self.name} 获取正在下载种子列表出错：{str(err)}")
            return [], True

    def get_completed_torrents(self, ids=None, tag=None):
        if not self._nxc:
            return [], True
        try:
            all_tasks = self._nxc.get_complete_torrents(ids=ids)
            if not all_tasks:
                return None, True
            else:
                return all_tasks, False
        except Exception as err:
            log.error(f"【{self.client_name}】{self.name} 获取已完成种子列表出错：{str(err)}")
            return [], True

    def get_files(self, tid=None):
        """
        读取种子文件列表
        """
        try:
            return self._nxc.get_files(tid)
        except Exception as err:
            log.error(f"【{self.client_name}】{self.name} 获取种子文件列表出错：{str(err)}")
            return None

    def set_torrents_status(self, ids, tags=None):
        return self.delete_torrents(ids=ids, delete_file=False)

    def get_transfer_task(self, tag, match_path=None):
        """
        获取需要转移的种子列表
        """
        torrents, error = self.get_completed_torrents()
        trans_tasks = []
        if error:
            return trans_tasks
        for torrent in torrents:
            name = torrent.name
            if not name:
                continue
            path = torrent.download_dir
            if not path:
                continue
            true_path, replace_flag = self.get_replace_path(path, self.download_dir)
            if match_path and not replace_flag:
                log.debug(f"【{self.client_name}】{self.name} 开启目录隔离，但 {torrent.name} 未匹配下载目录范围")
                continue
            trans_tasks.append({'path': os.path.join(true_path, name).replace("\\", "/"), 'id': torrent.id})
        return trans_tasks

    def get_remove_torrents(self, config):
        """
        获取需要清理的种子清单
        :param config: 删种策略
        :return: 种子ID列表
        """
        # 做种时间 单位：小时
        seeding_time = config.get("seeding_time")
        # 大小 单位：GB
        size = config.get("size")
        minsize = size[0] * 1024 * 1024 * 1024 if size else 0
        maxsize = size[-1] * 1024 * 1024 * 1024 if size else 0
        # 保存路径
        savepath_key = config.get("savepath_key")

        # 按下载状态筛选要改 nastools 源码才行，这里仅作冗余支持处理
        torrents, error = self.get_torrents(status=config.get("xl_state"))
        if error:
            return []
        date_now = self._nxc.check_server_now()
        remove_torrents = []
        remove_torrents_ids = []
        for torrent in torrents:
            if torrent.status == NasXunlei_Status.PHASE_TYPE_COMPLETE:
                torrent_seeding_time = date_now - torrent.update_time
            else:
                torrent_seeding_time = date_now - torrent.create_time
            if seeding_time and torrent_seeding_time < seeding_time * 3600:
                continue
            if size and (torrent.file_size >= maxsize or torrent.file_size <= minsize):
                continue
            if savepath_key and not re.findall(savepath_key, torrent.download_dir, re.I):
                continue
            remove_torrents.append({
                "id": torrent.id,
                "name": torrent.name,
                "site": "",
                "size": torrent.file_size
            })
            remove_torrents_ids.append(torrent.id)
        if config.get("samedata") and remove_torrents:
            remove_torrents_plus = []
            for remove_torrent in remove_torrents:
                name = remove_torrent.get("name")
                size = remove_torrent.get("size")
                for torrent in torrents:
                    if torrent.name == name and torrent.file_size == size and torrent.id not in remove_torrents_ids:
                        remove_torrents_plus.append({
                            "id": torrent.id,
                            "name": torrent.name,
                            "site": "",
                            "size": torrent.file_size
                        })
            remove_torrents_plus += remove_torrents
            return remove_torrents_plus
        return remove_torrents

    def add_torrent(self, content, download_dir=None, **kwargs):
        """
        添加下载任务
        """
        if not self._nxc:
            return False
        try:
            self._nxc.add_torrent(content=content, download_dir=download_dir)
            return True
        except Exception as err:
            log.error(f"【{self.client_name}】{self.name} 添加种子出错：{str(err)}")
            ExceptionUtils.exception_traceback(err)
            return False

    def start_torrents(self, ids):
        """
        下载控制：开始
        """
        if not self or not ids:
            return False
        try:
            self._nxc.start_torrents(ids=ids)
            return True
        except Exception as err:
            log.error(f"【{self.client_name}】{self.name} 开始下载出错：{str(err)}")
            return False

    def stop_torrents(self, ids):
        """
        下载控制：停止
        """
        if not self or not ids:
            return False
        try:
            self._nxc.stop_torrents(ids=ids)
            return True
        except Exception as err:
            log.error(f"【{self.client_name}】{self.name} 停止下载出错：{str(err)}")
            return False

    def delete_torrents(self, delete_file, ids):
        if not self or not ids:
            return False
        try:
            self._nxc.delete_torrents(ids=ids, delete_file=delete_file)
            return True
        except Exception as err:
            log.error(f"【{self.client_name}】{self.name} 删除种子出错：{str(err)}")
            return False

    def get_download_dirs(self):
        """
        获取下载目录清单
        """
        if not self._nxc:
            return []
        try:
            return self._nxc.get_download_dirs()
        except Exception as err:
            log.error(f"【{self.client_name}】{self.name} 获取下载目录清单出错：{str(err)}")
            return []

    def change_torrent(self, **kwargs):
        """
        修改种子状态
        """
        pass

    def get_downloading_progress(self, ids=None, **kwargs):
        """
        获取下载进度
        """
        torrents = self.get_downloading_torrents(ids=ids)
        DispTorrents = []
        for torrent in torrents:
            if torrent.status == NasXunlei_Status.PHASE_TYPE_RUNNING:
                state = "Downloading"
                speed = "%s%sB/s" % (chr(8595), StringUtils.str_filesize(torrent.speed))
            else:
                state = "Stoped"
                speed = "已暂停"
            DispTorrents.append({
                'id': torrent.id,
                'name': torrent.name,
                'speed': speed,
                'state': state,
                'progress': torrent.progress
            })
        return DispTorrents

    def set_speed_limit(self, download_limit=None, upload_limit=None):
        """
        设置速度限制
        """
        if not self._nxc:
            return False
        try:
            self._nxc.set_speed_limit(download_limit)
            return True
        except Exception as err:
            log.error(f"【{self.client_name}】{self.name} 设置速度限制出错：{str(err)}")
            return False

    def recheck_torrents(self, ids):
        """
        下载控制：重新校验
        """
        pass


class NasXunleiProvider:
    host = None
    common_header = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    }
    __xunlei_get_token = None

    def check_server_version(self) -> str:
        try:
            resp = self._get_as_json(url="/webman/3rdparty/pan-xunlei-com/index.cgi/launcher/status", with_auth=False)
            return str(resp.get('running_version'))
        except Exception as e:
            raise Exception("迅雷获取服务器版本失败", e)

    def _check_version_at_lest(self, current_version: str, target_version: str) -> bool:
        if current_version == target_version:
            return True
        current_version = self._parse_version(current_version)
        target_version = self._parse_version(target_version)
        index = 0
        while True:
            if len(current_version) <= index or len(target_version) <= index:
                return False
            if current_version[index] > target_version[index]:
                return True
            index += 1

    def _parse_version(self, version_name: str) -> list[int]:
        return [int(x) for x in version_name.split('.')]

    def check_server_now(self) -> int:
        resp = self._get_as_json(url="/webman/3rdparty/pan-xunlei-com/index.cgi/device/now", with_auth=False)
        return int(resp.get('now'))

    def info_watch(self):
        resp = self._post_as_json(
            url="/webman/3rdparty/pan-xunlei-com/index.cgi/device/info/watch",
            json_body={}
        )
        watch_info = SimpleNamespace()
        watch_info.target = resp.get("target")
        watch_info.client_version = resp.get("client_version")
        return watch_info

    def _get_torrents(self, filters):
        filters["type"] = {
            "in": "user#download-url,user#download"
        }
        resp = self._get_as_json(
            url="/webman/3rdparty/pan-xunlei-com/index.cgi/drive/v1/tasks",
            params={
                "filters": json.dumps(filters),
                "space": self.info_watch().target,
            }
        )
        all_tasks = []
        if resp.get("tasks") is None:
            return all_tasks
        for task in resp.get("tasks"):
            task_param = task.get("params")

            task_info = SimpleNamespace()
            task_info.space = task.get("space")
            task_info.id = task.get("id")
            task_info.type = task.get("type")
            task_info.file_id = task.get("file_id")
            task_info.create_time = parser.parse(task.get("created_time")).timestamp()
            task_info.update_time = parser.parse(task.get("updated_time")).timestamp()
            task_info.name = task.get("name")
            task_info.file_size = int(task.get("file_size"))
            task_info.speed = int(task_param.get("speed"))
            task_info.percent_done = int(task.get("progress")) / 100
            match task.get("phase"):
                case "PHASE_TYPE_RUNNING":
                    task_info.status = NasXunlei_Status.PHASE_TYPE_RUNNING
                case "PHASE_TYPE_PAUSED":
                    task_info.status = NasXunlei_Status.PHASE_TYPE_PAUSED
                case "PHASE_TYPE_PENDING":
                    task_info.status = NasXunlei_Status.PHASE_TYPE_PENDING
                case "PHASE_TYPE_ERROR":
                    task_info.status = NasXunlei_Status.PHASE_TYPE_ERROR
                case "PHASE_TYPE_COMPLETE":
                    task_info.status = NasXunlei_Status.PHASE_TYPE_COMPLETE
            task_info.hashString = task_param.get("info_hash")
            task_info.download_dir = task_param.get("real_path")

            all_tasks.append(task_info)

        return all_tasks

    def get_torrents(self, ids=None, status=None):
        filter = {
            "type": {
                "in": "user#download-url,user#download"
            }
        }
        if ids is list:
            filter["id"] = {
                "in": ids.join(",")
            }
        elif ids is str:
            filter["id"] = {
                "in": ids
            }
        if status is not None and len(status) > 0:
            filter["phase"] = {
                "in": status.join(",")
            }
        return self._get_torrents(filters=filter)

    def get_complete_torrents(self, ids):
        filter = {}
        if ids is list:
            filter["id"] = {
                "in": ids.join(",")
            }
        elif ids is str:
            filter["id"] = {
                "in": ids
            }
        filter["phase"] = {
            "in": "PHASE_TYPE_COMPLETE"
        }
        return self._get_torrents(filters=filter)

    def get_downloading_torrents(self, ids):
        filter = {}
        if ids is list:
            filter["id"] = {
                "in": ids.join(",")
            }
        elif ids is str:
            filter["id"] = {
                "in": ids
            }
        filter["phase"] = {
            "in": "PHASE_TYPE_PENDING,PHASE_TYPE_RUNNING,PHASE_TYPE_PAUSED,PHASE_TYPE_ERROR"
        }
        return self._get_torrents(filters=filter)

    def add_torrent(self, content, download_dir):
        if not isinstance(content, str):
            torrent_link = Torrent.binary_data_to_magnet_link(content)
            torrent_link = torrent_link.replace("%3A", ":")
            return self.add_torrent(torrent_link, download_dir)

        target = self.info_watch().target
        try:
            torrent_info = self._post_as_json(
                url="/webman/3rdparty/pan-xunlei-com/index.cgi/drive/v1/resource/list",
                json_body={
                    "urls": content,
                }
            )
        except Exception as err:
            raise Exception("迅雷获取种子文件列表失败", err)
        path_id = self._get_path_id(target, download_dir)
        error = None
        for torrent_item in torrent_info.get("list").get("resources"):
            try:
                self._post_as_json(
                    url="/webman/3rdparty/pan-xunlei-com/index.cgi/drive/v1/task",
                    json_body={
                        "type": "user#download-url",
                        "name": torrent_item.get("name"),
                        "file_name": torrent_item.get("file_name"),
                        "file_size": str(torrent_item.get("file_size") if torrent_item.get("file_size") is not None else 0),
                        "space": target,
                        "params": {
                            "target": target,
                            "url": torrent_item.get("meta").get("url"),
                            "total_file_count": str(torrent_item.get("file_count")),
                            "sub_file_index": self._get_file_index(torrent_item),
                            "file_id": "",
                            "parent_folder_id": path_id,
                        }
                    }
                )
            except Exception as err:
                error = Exception("迅雷提交任务失败", err)
        if error is not None:
            raise error

    def _get_path_id(self, space_id, path: str):
        try:
            parent_id = ""
            dir_list = path.split('/')
            while '' in dir_list:
                dir_list.remove('')
            cnt = 0
            while 1:
                if len(dir_list) == cnt:
                    return parent_id
                dirs = self._get_as_json(
                    url="/webman/3rdparty/pan-xunlei-com/index.cgi/drive/v1/files",
                    params={
                        "filters": json.dumps({
                            "kind": {
                                "eq": "drive#folder"
                            }
                        }),
                        "space": space_id,
                        "parent_id": parent_id,
                        "limit": 200,
                    }
                )
                if parent_id == "":
                    parent_id = dirs['files'][0]['id']
                    continue

                exists = False
                if 'files' in dirs.keys():
                    for dir_now in dirs['files']:
                        if dir_now['name'] == dir_list[cnt]:
                            cnt += 1
                            exists = True
                            parent_id = dir_now['id']
                            break

                if exists:
                    continue

                parent_id = self._create_sub_path(space_id, dir_list[cnt], parent_id)
                if parent_id is None:
                    return None
                cnt += 1
        except Exception as err:
            raise Exception("获取目录 ID 失败", err)

    def _create_sub_path(self, space_id, dir_name: str, parent_id: str) -> TypeError:
        try:
            rep = self._post_as_json(
                url='/webman/3rdparty/pan-xunlei-com/index.cgi/drive/v1/files',
                json_body={
                    "parent_id": parent_id,
                    "name": dir_name,
                    "space": space_id,
                    "kind": "drive#folder",
                }
            )
            return rep['file']['id']
        except Exception as err:
            raise Exception("创建目录失败", err)

    def _get_file_index(self, file_info) -> str:
        file_count = int(file_info['file_count'])
        if file_count == 1:
            return '--1,'
        return '0-' + str(file_count - 1)

    def get_files(self, tid):
        filters = None
        if tid is not None:
            filters = {
                "id": {
                    "in": tid
                }
            }
        task = self._get_torrents(filters=filters)
        if len(task) >= 1:
            task = task[0]
        else:
            raise Exception(f"No task id of {tid}")
        resp = self._get_as_json(
            url=f"{self.host}/webman/3rdparty/pan-xunlei-com/index.cgi/drive/v1/files",
            params={
                "pan_auth": self._get_token(),
                "parent_id": task.file_id
            }
        )
        files = resp.get("files")
        result = []
        for file in files:
            info = SimpleNamespace()
            info.id = file.get("id")
            info.name = file.get("name")
            info.size = int(file.get("size"))
            result.append(info)
        return result

    def get_download_dirs(self):
        resp = self._get_as_json(
            url="/webman/3rdparty/pan-xunlei-com/index.cgi/device/download_paths"
        )
        dirs = []
        for dir in resp:
            dirs.append(dir.get("RealPath"))
        return dirs

    def set_speed_limit(self, speed):
        self._post_as_json(
            url="/webman/3rdparty/pan-xunlei-com/index.cgi/drive/v1/resource/list",
            json_body={
                "speed_limit": speed,
            }
        )

    def _set_task_status(self, ids, status):
        if ids is str:
            ids = [ids]
        torrents = self.get_torrents(ids=ids)
        has_failed_id = None
        for torrent in torrents:
            try:
                self._post_as_json(
                    url="/webman/3rdparty/pan-xunlei-com/index.cgi/method/patch/drive/v1/task",
                    json_body={
                        "id": torrent.id,
                        "space": torrent.space,
                        "type": torrent.type,
                        "set_params": {
                            "spec": json.dumps({
                                "phase": status
                            })
                        }
                    }
                )
            except Exception as err:
                has_failed_id = err
        if has_failed_id is not None:
            raise has_failed_id

    def start_torrents(self, ids):
        self._set_task_status(ids=ids, status="running")

    def stop_torrents(self, ids):
        self._set_task_status(ids=ids, status="pause")

    def delete_torrents(self, ids, delete_file):
        if delete_file:
            self._set_task_status(ids, "delete")
        else:
            target = self.info_watch().target
            url = f"/webman/3rdparty/pan-xunlei-com/index.cgi/method/delete/drive/v1/tasks?space={target}"
            if isinstance(ids, str):
                ids = [ids]
            for id in ids:
                url = f"{url}&task_ids={id}"
            self._post_as_json(url=url, json_body={})

    _token_time = 0
    _token_str = None
    def _get_token(self):
        current_version = self.check_server_version()
        if self._check_version_at_lest(current_version, "3.21.0"):
            return self._get_token_from_html()
        return self._create_new_token()

    def _create_new_token(self):
        return self.__xunlei_get_token.GetXunLeiToken(self.check_server_now())

    def _get_token_from_html(self):
        if int(time.time()) - self._token_time <= 60:
            return self._token_str
        resp = self._get(url="/webman/3rdparty/pan-xunlei-com/index.cgi/", with_auth=False)
        uiauth = r"function uiauth(.*)}"
        for script in re.findall(uiauth, resp):
            script = "function uiauth%s}" % script
            context = js2py.EvalJs()
            context.execute(script)
            self._token_str = context.uiauth("any")
            self._token_time = int(time.time())
            return self._token_str
        raise Exception("从 HTML 中获取 uiauth 失败")

    def _post_as_json(self, url: str, json_body=None):
        xtoken = self._get_token()
        headers = dict(**self.common_header)
        headers["pan-auth"] = xtoken
        url = f"{self.host}{url}{'?' if '?' not in url else '&'}pan_auth={xtoken}&device_space="
        url = url.replace("#", "%23")
        resp = RequestUtils(headers=headers).post(
            url=url,
            json=json_body,
        )
        return self._as_checked_json(resp)

    def _get(self, url, params=None, with_auth=True):
        if params is None:
            params = {}
        headers = dict(**self.common_header)
        if with_auth:
            xtoken = self._get_token()
            params["pan_auth"] = xtoken
            headers["pan-auth"] = xtoken
        params["device_space"] = ""
        resp = RequestUtils(headers=headers).get(
            url=f"{self.host}{url}",
            params=params
        )
        return str(resp)

    def _get_as_json(self, url, params=None, with_auth=True):
        return self._as_checked_json(self._get(url, params, with_auth))

    def _as_checked_json(self, result):
        if result is not None:
            try:
                if isinstance(result, requests.models.Response):
                    result = result.json()
                else:
                    result = json.loads(str(result))
            except Exception as err:
                if isinstance(result, requests.models.Response):
                    log.debug(f"【NAS 迅雷】响应解析失败：{result.text}")
                else:
                    log.debug(f"【NAS 迅雷】响应解析失败：{result}")
                raise Exception("响应 json 解析失败，请检查控制台输出日志。", err)
            if result.get("error_code") is not None and int(result.get("error_code")) != 0:
                if "permission_deny" in result.get('error'):
                    raise Exception("签名算法失效，请根据 README.md 中提示进行操作后再试。")
                else:
                    raise Exception(f"请求失败：{result.get('error')}")
        return result

    def __init__(self, host, port, username, password):
        self.host = host
        if self.host is not None and not str(self.host).startswith("http"):
            self.host = f"http://{self.host}"
        if str(port).isdigit():
            self.host = f"{self.host}:{port}"
        if username is not None and password is not None:
            basic = base64.b64encode(f'{username}:{password}'.encode('utf-8')).decode('utf-8')
            self.common_header["Authorization"] = f"Basic {basic}"
        # https://github.com/opennaslab/kubespider/blob/f55eab6a931d1851d5cbe2b6467d7dde96bffdef/.config/dependencies/xunlei_download_provider/get_token.js
        xunlei_get_token = os.path.join(Config().get_config_path(), "xunlei_get_token.js")
        __xunlei_get_token_js_external = """
// 这部分代码不要动 -- start
iB = {
    exports: {}
},
lB = {
    exports: {}
};

var g$ = {
    utf8: {
        stringToBytes: function(e) {
            return g$.bin.stringToBytes(unescape(encodeURIComponent(e)))
        },
        bytesToString: function(e) {
            return decodeURIComponent(escape(g$.bin.bytesToString(e)))
        }
    },
    bin: {
        stringToBytes: function(e) {
            for (var t = [], n = 0; n < e.length; n++) t.push(e.charCodeAt(n) & 255);
            return t
        },
        bytesToString: function(e) {
            for (var t = [], n = 0; n < e.length; n++) t.push(String.fromCharCode(e[n]));
            return t.join("")
        }
    }
},
_N = g$;

var e = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
t = {
    rotl: function(n, r) {
        return n << r | n >>> 32 - r
    },
    rotr: function(n, r) {
        return n << 32 - r | n >>> r
    },
    endian: function(n) {
        if (n.constructor == Number) return t.rotl(n, 8) & 16711935 | t.rotl(n, 24) & 4278255360;
        for (var r = 0; r < n.length; r++) n[r] = t.endian(n[r]);
        return n
    },
    randomBytes: function(n) {
        for (var r = []; n > 0; n--) r.push(Math.floor(Math.random() * 256));
            return r
    },
    bytesToWords: function(n) {
        for (var r = [], o = 0, a = 0; o < n.length; o++, a += 8) r[a >>> 5] |= n[o] << 24 - a % 32;
            return r
    },
    wordsToBytes: function(n) {
        for (var r = [], o = 0; o < n.length * 32; o += 8) r.push(n[o >>> 5] >>> 24 - o % 32 & 255);
            return r
    },
    bytesToHex: function(n) {
        for (var r = [], o = 0; o < n.length; o++) r.push((n[o] >>> 4).toString(16)), r.push((n[o] & 15).toString(16));
            return r.join("")
    },
    hexToBytes: function(n) {
        for (var r = [], o = 0; o < n.length; o += 2) r.push(parseInt(n.substr(o, 2), 16));
            return r
    },
    bytesToBase64: function(n) {
        for (var r = [], o = 0; o < n.length; o += 3)
            for (var a = n[o] << 16 | n[o + 1] << 8 | n[o + 2], i = 0; i < 4; i++) o * 8 + i * 6 <= n.length * 8 ? r.push(e.charAt(a >>> 6 * (3 - i) & 63)) : r.push("=");
                return r.join("")
    },
    base64ToBytes: function(n) {
        n = n.replace(/[^A-Z0-9+\/]/ig, "");
        for (var r = [], o = 0, a = 0; o < n.length; a = ++o % 4) a != 0 && r.push((e.indexOf(n.charAt(o - 1)) & Math.pow(2, -2 * a + 8) - 1) << a * 2 | e.indexOf(n.charAt(o)) >>> 6 - a * 2);
            return r
    }
};
lB.exports = t

var L8e = function(e) {
    return e != null && (sB(e) || D8e(e) || !!e._isBuffer)
};

function sB(e) {
    return !!e.constructor && typeof e.constructor.isBuffer == "function" && e.constructor.isBuffer(e)
}

function D8e(e) {
    return typeof e.readFloatLE == "function" && typeof e.slice == "function" && sB(e.slice(0, 0))
}

function GetTokenInternal(a, i) {
    var e = lB.exports,
    t = _N.utf8,
    n = L8e,
    r = _N.bin,
    o = function(a, i) {
        a.constructor == String ? i && i.encoding === "binary" ? a = r.stringToBytes(a) : a = t.stringToBytes(a) : n(a) ? a = Array.prototype.slice.call(a, 0) : !Array.isArray(a) && a.constructor !== Uint8Array && (a = a.toString());
        for (var l = e.bytesToWords(a), u = a.length * 8, s = 1732584193, d = -271733879, f = -1732584194, h = 271733878, v = 0; v < l.length; v++) l[v] = (l[v] << 8 | l[v] >>> 24) & 16711935 | (l[v] << 24 | l[v] >>> 8) & 4278255360;
        l[u >>> 5] |= 128 << u % 32, l[(u + 64 >>> 9 << 4) + 14] = u;
        for (var g = o._ff, w = o._gg, y = o._hh, b = o._ii, v = 0; v < l.length; v += 16) {
            var $ = s,
                S = d,
                _ = f,
                k = h;
            s = g(s, d, f, h, l[v + 0], 7, -680876936), h = g(h, s, d, f, l[v + 1], 12, -389564586), f = g(f, h, s, d, l[v + 2], 17, 606105819), d = g(d, f, h, s, l[v + 3], 22, -1044525330), s = g(s, d, f, h, l[v + 4], 7, -176418897), h = g(h, s, d, f, l[v + 5], 12, 1200080426), f = g(f, h, s, d, l[v + 6], 17, -1473231341), d = g(d, f, h, s, l[v + 7], 22, -45705983), s = g(s, d, f, h, l[v + 8], 7, 1770035416), h = g(h, s, d, f, l[v + 9], 12, -1958414417), f = g(f, h, s, d, l[v + 10], 17, -42063), d = g(d, f, h, s, l[v + 11], 22, -1990404162), s = g(s, d, f, h, l[v + 12], 7, 1804603682), h = g(h, s, d, f, l[v + 13], 12, -40341101), f = g(f, h, s, d, l[v + 14], 17, -1502002290), d = g(d, f, h, s, l[v + 15], 22, 1236535329), s = w(s, d, f, h, l[v + 1], 5, -165796510), h = w(h, s, d, f, l[v + 6], 9, -1069501632), f = w(f, h, s, d, l[v + 11], 14, 643717713), d = w(d, f, h, s, l[v + 0], 20, -373897302), s = w(s, d, f, h, l[v + 5], 5, -701558691), h = w(h, s, d, f, l[v + 10], 9, 38016083), f = w(f, h, s, d, l[v + 15], 14, -660478335), d = w(d, f, h, s, l[v + 4], 20, -405537848), s = w(s, d, f, h, l[v + 9], 5, 568446438), h = w(h, s, d, f, l[v + 14], 9, -1019803690), f = w(f, h, s, d, l[v + 3], 14, -187363961), d = w(d, f, h, s, l[v + 8], 20, 1163531501), s = w(s, d, f, h, l[v + 13], 5, -1444681467), h = w(h, s, d, f, l[v + 2], 9, -51403784), f = w(f, h, s, d, l[v + 7], 14, 1735328473), d = w(d, f, h, s, l[v + 12], 20, -1926607734), s = y(s, d, f, h, l[v + 5], 4, -378558), h = y(h, s, d, f, l[v + 8], 11, -2022574463), f = y(f, h, s, d, l[v + 11], 16, 1839030562), d = y(d, f, h, s, l[v + 14], 23, -35309556), s = y(s, d, f, h, l[v + 1], 4, -1530992060), h = y(h, s, d, f, l[v + 4], 11, 1272893353), f = y(f, h, s, d, l[v + 7], 16, -155497632), d = y(d, f, h, s, l[v + 10], 23, -1094730640), s = y(s, d, f, h, l[v + 13], 4, 681279174), h = y(h, s, d, f, l[v + 0], 11, -358537222), f = y(f, h, s, d, l[v + 3], 16, -722521979), d = y(d, f, h, s, l[v + 6], 23, 76029189), s = y(s, d, f, h, l[v + 9], 4, -640364487), h = y(h, s, d, f, l[v + 12], 11, -421815835), f = y(f, h, s, d, l[v + 15], 16, 530742520), d = y(d, f, h, s, l[v + 2], 23, -995338651), s = b(s, d, f, h, l[v + 0], 6, -198630844), h = b(h, s, d, f, l[v + 7], 10, 1126891415), f = b(f, h, s, d, l[v + 14], 15, -1416354905), d = b(d, f, h, s, l[v + 5], 21, -57434055), s = b(s, d, f, h, l[v + 12], 6, 1700485571), h = b(h, s, d, f, l[v + 3], 10, -1894986606), f = b(f, h, s, d, l[v + 10], 15, -1051523), d = b(d, f, h, s, l[v + 1], 21, -2054922799), s = b(s, d, f, h, l[v + 8], 6, 1873313359), h = b(h, s, d, f, l[v + 15], 10, -30611744), f = b(f, h, s, d, l[v + 6], 15, -1560198380), d = b(d, f, h, s, l[v + 13], 21, 1309151649), s = b(s, d, f, h, l[v + 4], 6, -145523070), h = b(h, s, d, f, l[v + 11], 10, -1120210379), f = b(f, h, s, d, l[v + 2], 15, 718787259), d = b(d, f, h, s, l[v + 9], 21, -343485551), s = s + $ >>> 0, d = d + S >>> 0, f = f + _ >>> 0, h = h + k >>> 0
        }
        return e.endian([s, d, f, h])
    };
    o._ff = function(a, i, l, u, s, d, f) {
    var h = a + (i & l | ~i & u) + (s >>> 0) + f;
    return (h << d | h >>> 32 - d) + i
    }, o._gg = function(a, i, l, u, s, d, f) {
    var h = a + (i & u | l & ~u) + (s >>> 0) + f;
    return (h << d | h >>> 32 - d) + i
    }, o._hh = function(a, i, l, u, s, d, f) {
    var h = a + (i ^ l ^ u) + (s >>> 0) + f;
    return (h << d | h >>> 32 - d) + i
    }, o._ii = function(a, i, l, u, s, d, f) {
    var h = a + (l ^ (i | ~u)) + (s >>> 0) + f;
    return (h << d | h >>> 32 - d) + i
    }, o._blocksize = 16, o._digestsize = 16, iB.exports = function(a, i) {
    if (a == null) throw new Error("Illegal argument " + a);
    var l = e.wordsToBytes(o(a, i));
    return i && i.asBytes ? l : i && i.asString ? r.bytesToString(l) : e.bytesToHex(l)
    }

    return iB.exports(a, i)
}
// 这部分代码不要动 -- end

// 部分代码根据手册修改 -- start
function GetXunLeiToken(e) {
    return rV(e)
}

var DRe = GetTokenInternal
// 这部分代码根据手册修改 -- end

// 这部分代码从迅雷网站js脚本中拷贝 -- start
function NRe() {
    return ""
}
function FRe() {
    return "idbvrxjhrbzjjuyfkfdokrdcizdclpjjydsynoqyumcutwhpclnbmhcglwhkkovpwroqibazfcnaeayzgfqfelaywiomwyjnagnrrddmuexargwokjpwbikeprjolmnyqrusrlvzhpuyjnsrqmqstkisjbuexfyyxxzluuyxifamyerueuyrcnjnjejdzfirnbhocnmffibvtpclljmcqlukrbrptojadixndwajouvlpqpwimzbbyppdqxxxhovokyukgkxrayfuyocvspxmmgezpruqgqnbrrxlqvrppbzljpfnpcdjktuoegplnmgzaaeezkqcgzhbohygiimggkvezfsmbrtkdygmjmbxmgvzajkxrdpucquyvefuflvpzxixoutccgppkzvoosshhyuriwdgchymguwgvkoaedcgyjybyxmrlsdfhvmjcucpidjqidhqjnnnovfkxdkpfkfoedaqlhptgaceyueeqscjnwzomnypijnsyfqozpdcazvjvbxxaiybxbjizistxuqxtjixzpvrcqkfrcbfxjifemigcoppiggitjylsascaqgqozmurbfborpovagwmcpzpjugdthbzvrjhntovigecytyfraphdmaaojkijhnhhqdkscyshxbtmfycajpzmfhbmqvkrvmuestzgdwwisdwbfvcdyzg"
}
function xRe() {
    return "lywoqrspljeop"
}
function RRe() {
    return "ghuxmhchesxqwlwwwjamsyrpyraelwepuvkwjuacmfacpbjqteeqdfquphhltofphsffjskkvmxtlxsjtakactyvhvjgochfkfxuzyyguxzcaedwgvrbtcomuwowpqvhrlpruavwyoaoawttjexduuroqmpbfrepkeybtppmdsmforqwhdpdeafpqmuhrkhccqkqsbtrzszfwohcqsowgyehscfzlfygearpolgifwcipdmgcydukutomtmplitahhdhikujprbraszvjaponzlhbjvsxvawtkdlgmegeaqvsrgwoblenrqdiomqovnxwgosqhassfqxmrljgskicqfwtxyzalsbzbdrqlgdinqgqdfruhpcidbqwfwgvyefaepvxjuqvhs"
}
function LRe() {
    return "fcbdlozmubsxlkpvviangcwxusuchhffqbwzwahyoymqxjuzhoihstqfiabjnumyuflywjkwqqlkrcrkjhwwnsejsqprbiytufgfeuqcggdusgapbboqdpjdoaxuzsojffqztpokphaydlpaawhzhylsjefgaamnaqzvblkwikhqmbgrlzmvqhnzgsjzayeprliqlourmowxrchqrtsyjiahopwpjgqnucohokrfnhhswuartcmkzmwdyoixfvozlzwgpjemkanvbpukdtzqcdtwnmlusphagsajggewzfqpbcil"
}
function BRe() {
    return "tsibbbxtpeoscmiorljeffkrykofdbaankashzytiilzaxuxkfshxjpzdmzvhnxzqljnhisjnnvppcsxdsjcxgwehofmklevahmktbrwciajxvkuogdjhrehqhamquflyxoxrbuzklihvivggglspgczbslpllklsreixkjbzoafeidyibknhjxgunsdikbakhuksqfulzdfwwknjcaayspaihwdxlzefymtuvpwuraxngfromwiwmfbyv"
}
function VRe() {
    return "jznhn"
}
function jRe() {
    return "yarctazbvmcltxokotwxzvairtkxeghigjphgwbmfgzweaclxcgflgydsmsfojpspfcsybtgjrxogcmsnsmcfngyyhrvsybtr"
}
function HRe() {
    return "ldztnnleeapkyobyalxatvphmfsjloxltccqtdawxfybmofrqwckjzdsfnfannpwhmwgzqbqzymczruh"
}
function zRe() {
    return "qaqpxduqarmdqladmhsrdkbgkrtsvuxtibuvncmnekhpyunnmvxqhdrvkjgwbtsipngpzomtcigjrmookykfqottquk"
}
function URe() {
    return "sfvmzsgqivrwguluzfxxvifyodjvyfb"
}
function WRe() {
    return "hcrmylfxnwhafwxlmxt"
}
function qRe() {
    return "mmoqbwhgzuiwxmpdi"
}
function KRe() {
    return "pqzxlqwfp"
}
function GRe() {
    return "fozeh"
}
function YRe() {
    return "akxdxaf"
}
function XRe() {
    return "dyczfcv"
}
function rV(e) {
    return e + "." + DRe(e + NRe() + FRe() + xRe() + RRe() + LRe() + BRe() + VRe() + jRe() + HRe() + zRe() + URe() + WRe() + qRe() + KRe() + GRe() + YRe() + XRe())
}
// 这部分代码从迅雷网站js脚本中拷贝 -- end

"""
        if os.path.exists(xunlei_get_token):
            with open(xunlei_get_token) as f:
                __xunlei_get_token_js_external = ""
                for js_line in f.readlines():
                    __xunlei_get_token_js_external = __xunlei_get_token_js_external + "\n" + js_line
        context = js2py.EvalJs()
        context.execute(__xunlei_get_token_js_external)
        self.__xunlei_get_token = context

