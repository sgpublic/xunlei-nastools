import os.path
from abc import ABCMeta
from enum import Enum

from app.conf import ModuleConf
from app.utils import PathUtils


class Downloader_NasXunlei(Enum):
    NAS_XUNLEI = "NAS 迅雷"


_nas_xunlei_icon = ("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAYAAACtWK6eAAAAAXNSR0IArs4c6QAADQtJREFUeF7tnU1yHDcShVHVvICD8trSbobhO5A8icS9GTE3oHgDR7T2bp1E1B0ctHdur0eMuYBYmEF1dU+zWT9AAqjKTDwuSQAFvMyPyARQqMrgBwpAgUEFKmgDBaDAsAIABN4BBUYUACBwDygAQOADUICmAGYQmm6oVYgCAKQQQ2OYNAUACE031CpEAQBSiKExTJoCAISmG2oVogAAKcTQGCZNAQBC0w21ClEAgBRiaAyTpgAAoemGWoUoAEAKMTSGSVMAgNB0Q61CFAAghRgaw6QpAEBouqFWIQoAkEIMjWHSFAAgNN1QqxAFAEghhpY+zIvbbx+MqS4f1+c3c44FgMypNp4VpMDPv/z7qqnq98aYD65is6rf/fnrD9ugRiILA5BIAVE9vQJutrDGvK9MdfX/1u3N4/rNJv3TxlsEIHMrjucNKtCFUXfGmLcnhTZzh1b75wMQOOyiCvzjX/95Wz83Doo2jOr52T6uz98t1UkAspTyhT/X5RfPVXX3Mox6LUptm+vfP/34sJRcAGQp5Qt9ri8YrTzWfHz8dH6/pFQAZEn1C3p2f+I9LIA19uGP9ZvrpSUCIEtbQPnzQ8Ho5Fg07zg2CQBR7qBLDW9kRWqyS0vnHQBk0kQoQFUgBgwueQcAoVof9QYViAZj1zKb0Go/UIRYcPooBYg5Ru8zlzhKMjV4ADKlEP7eq0DQcq2XhsscJZnqGgCZUgh/f6FAejDa5hc7SjJlXgAypRD+3irgjoRUz8+/Te18E+Ril3cgSSdYseQqF7dPv42clYqShtOSbt9AMINEmVd35Ytfnu5MZT5mGyWDoyRTYwMgUwoV+PdES7ajynE5SjJlXgAypVBBf8+UgPcpyDrvQA5SkNP7DDVjAt77eO55BwDx8ZpCymTPM051FJB3AJBCnH9smN"
                    "2FCG516vT11pzqiAmt9iIgB8npDgzbnjucOpZAUmgFQBg6b+4uzR5OnQzIrVy5X1W2elj6TUFfrTGD+ColuNxC4dSYYmyPlpx2GoAIdvypri8ZTo30TVQeAkCmvEzo35cOp4Zkk5aHABChAAx1e8bNvnDlhC3xtvlS+ChRg6sCXGeNTi9RoRVWsbh6OaFfrGeNbjzSQisAQnBEjlWYzxo7yQSGVmoA2Z08baPFS2PM0W3ghx3irTW2vTK/MuZzs1o9zH2Ffg6wGC7dDg1TZGglGpDYiwLchpXbrKpN83XJe1+p4OR8gYnap6F6HC9iCBkjqyTdrdufff/+tqmq3fkgW/1kqsNMsJ8dMpwdsjcSZhZBs4b40Cr7DNLr7Ls4p3Vwa+zbynQgzHtgbjAU+B+R91xBkTRrdPZlcbduyGzRV3ZyBnGO7iqO/Gfn6OxkXVz4tbL2nkvoJWGFqkds0XnH8XgGAWmnc1Nf2spedf/pM4Q2ZD/OXtGBYlermyUTehErVD2WkLqkS5pB9pUOIVNx0Mx/oRnTM1R+/5QEL+lGAdJX2c0y7vfqZ5oZjd5dmOBeZJL4oya0ypakqw3NrPnYnNWfc4Zc/7z99iXDxWyzgaYptMoGyKk1NAGTKy8Rt3zbh9yMs+xsxC9xWHEPjKnar5pKTPy3zaq+TjWTSE3ET5xUXWg12wwyRrtgWKIhEZ2InxhV+m75mI9O7oPMNZ11Ycb77jyVhJmFDEk31i9zaZv1OUpDKxYzyJDh5rj6MpHTbJpVfR8SbikJqVr5pFwfGmNrNjPI0DJyU9W8Z5WA/6DSV6l6bLQxxn6trd1+PzvbhvyjiHHaOeuyBuRYiO4/L8/EfgISFatU416JJH1OaoeexTt2799x1xRSDdlF4/4H6xxkIjdhu8t8upqjMKR6bZqAEJPDP9nQPogJsdzABPw3ble2XF8zfa4s1L65y6sNrWTOILm/eJTGnTa5PleWpnvpWtG8/yETkIzfykvnNoW0pD"
                    "y0EglIETG9AL5K2P8QCcjF7ZMV4D/au6g+7zg2oKwkHYAsDp/mJd0+ccUA4g731c/NX4t7SMkdKCTvEDmD8N4kLIKaokIrcTmIgD0Q1ZSUFloBENXunHhwBYZW4gDBEm9ip/dvrsjQShwgWOL19+iUJUvYLR/TS8QqFlawUrp8QFsFh1aiZhAAEuDUCYvub8HPfd1Rwi4nb0rEDIIVrOR2D27w+JMRWt8eFLtRCECC/Tl7hf0l39phETGDYAUru79HPUAzLCIAwQpWlP/OWlkbLOwBQYI+q3+nftimts1nLt9aoQyOPSA4g0UxK686klfD2AMi/HMAvDyVQW9aWAR9bRiAMHCaUrsgIV8BIKV6J7dxz/D9FcqQ+QMi4yYTivao06MAtxAMgMBN2SrA4YvD/AG5/fbBmIrtbYpsvUtRx5ZcBQMgihyphKHMndgDkBK8SuEY58pV2AOCjUKF3p14SDlzFfaA4KhJYm9S3FyOWYU9IM6eF7dP7j4sCd8tVOx+woaWaF9FCiBuFct9XQo/UCBIgdjwSwggWOoN8goUfqUANfwSAQjCLHh8QgW2xtj7ZrV68PnoKABJqDyaEqfA5Ge85QCCM1nivE9Mh0euNxIDCPZDxLibpI5OvvEoBpAuD8FqliT349nXjTH26+P6jfuW5OSPKEAwi0zaEwX6FQiC4rgJUYBgNQv+76sAdVn3tH2BgGBPxNdJCi03uTIVoos4QDCLhJhXVNlt11vKkaLJZJuqhEhAkItQzc263rZZ1df18/OVNeZ9ZSoHyhgs5LwiRAWRgLSzCPZFQuwspWwLyX6H2135dALLLFCITtKPO49TvlL8PqyffR/tca89+BwNCXvSdGmxM4gbGkKtaQNLLcHly1aiAUGoxdX97Y0x1aUx5or4Hk/SlagYlcQDglWtGPNnq3vIJbpc0b3LM7U6NXt+4TN6FYB0r+V+8TCCjyYok0aBFwm3C4efq+quMpWbVdqfVJt5abrb34oKQNzQAEl"
                    "ONyG3/QKSQ95o6ksp3z1UAwggITtx7oqvIMn9wJTtqwJkl4+0R1HuEG5FuYnb1Z7KGXwewDKv8On4vow6QI5WtnwSwxCtiijr8oI/1m+uif9oNsaarZTwycegKgEBJD6mHy5zvAfR7TW593CGZpR2lvB9xzuuZ/PXVgvIISGs6jHjzq+4iCfam9MXio5WodylB2qBODWPakAACY3GfZhFq62rlnpACljdcgn1w7FbWmNfhUOVqfbHyV96sDW731f27/0ftIZLFHSLAGQvzMXtk8p32rmcW6I4IPc6RQGidhl45Noa7g7IvX/FAaI15MIskge1IgE5hFy7l66U7Je8XnnK4zJltVo0IJpWubDylAfc4gHRlMAjzEoPCQA50tRj1zi9BdK2uHlcn9+kbbLs1gBIj/0lLwdjFkkLNAAZ0FPubIJkPSUiAGRCTWmzCZL1lHgYA0A89JQ2myDM8jCqZxEA4inUbhe+PapCvakj4EmxRRFmxSq4rw9AApWUMJsgzAo06khxAELUkvjGHfFp4dUQZoVr1lcDgETo2N2k4t5/Zxh2IcyKMO2hKgBJoCLTsAubhglsC0ASiLhvglvYhTAr3rgAJF7DVy1wWe2qbXP9+6cfX7xtmGG4qpsEIJnMyyI/wYtU0dYFINESjjfQdydt5kcemsdyb7zSACReQ68WlkrkkYd4mWewEACJ0y+4dsDnAILb7q+A5d4YIQFIjHrEujPPJljuJdrJVQMgEeLFVp1pNtk+rs/fxfa11PoAZGHLzzGbIA+hGxmA0LVLWjPveyfIQ6jGAiBU5TLUy/jtd+QhRHsBEKJwuarlykse1+ewNcFoEI0gWu4qOfIS5CE0qwEQmm7Za6X/KCnyEIrRAAhFtZnqJIYEeQjBbgCEINrcVS5un/5K8VFN5CHhlgMg4ZotUiPFMjDykHDTAZBwzRarEQ8J8pBQ4wGQUMUWLh8JCfKQQPsBkEDBOBSnbiji/ZBw6wGQcM1Y1KBCgjwkzHw"
                    "AJEwvVqUpkOA99TATApAwvdiVDocEiXqIEQFIiFpMywZCgkQ9wI4AJEAszkUDIMELVAGGBCABYnEv6gsJEnV/SwIQf61ElPSDBHmIrzEBiK9SgspNQoIL5bytCUC8pZJVcAwSbBj62xKA+GslruQYJDjZ62dOAOKnk9hSQ5AgUfczKQDx00l0qX5IkKj7GBWA+KikoEwPJNgw9LArAPEQSUuRY0iQqPtZFYD46aSm1DEkSNSnzQpApjVSV2IPCRL1adMCkGmNVJZwkDRn9ec/f/1hq3KAiQYFQBIJiWZ0KgBAdNoVo0qkAABJJCSa0akAANFpV4wqkQIAJJGQaEanAgBEp10xqkQKAJBEQqIZnQoAEJ12xagSKQBAEgmJZnQqAEB02hWjSqQAAEkkJJrRqQAA0WlXjCqRAgAkkZBoRqcCAESnXTGqRAoAkERCohmdCgAQnXbFqBIpAEASCYlmdCoAQHTaFaNKpAAASSQkmtGpAADRaVeMKpEC/wWd5o4U2bMVfwAAAABJRU5ErkJggg==")
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
            "placeholder": "5055"
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


class NasXunlei(metaclass=ABCMeta):
    # 下载器ID
    client_id = "nas_xunlei"
    # 下载器类型
    client_type = Downloader_NasXunlei.NAS_XUNLEI
    # 下载器名称
    client_name = Downloader_NasXunlei.NAS_XUNLEI.value

    @classmethod
    def match(cls, ctype):
        return True if ctype in [cls.client_id, cls.client_type, cls.client_name] else False

    # @abstractmethod
    def get_type(self):
        return self.client_type

    # @abstractmethod
    def connect(self):
        if self.host and self.port:
            feapder


    def __login_qbittorrent(self):
        pass

    # @abstractmethod
    def get_status(self):
        """
        检查连通性
        """
        pass

    # @abstractmethod
    def get_torrents(self, ids, status, tag):
        """
        按条件读取种子信息
        :param ids: 种子ID，单个ID或者ID列表
        :param status: 种子状态过滤
        :param tag: 种子标签过滤
        :return: 种子信息列表，是否发生错误
        """
        pass

    # @abstractmethod
    def get_downloading_torrents(self, ids, tag):
        """
        读取下载中的种子信息，发生错误时需返回None
        """
        pass

    # @abstractmethod
    def get_completed_torrents(self, ids, tag):
        """
        读取下载完成的种子信息，发生错误时需返回None
        """
        pass

    # @abstractmethod
    def get_files(self, tid):
        """
        读取种子文件列表
        """
        pass

    # @abstractmethod
    def set_torrents_status(self, ids, tags=None):
        """
        迁移完成后设置种子标签为 已整理
        :param ids: 种子ID列表
        :param tags: 种子标签列表
        """
        pass

    # @abstractmethod
    def get_transfer_task(self, tag, match_path=None):
        """
        获取需要转移的种子列表
        """
        pass

    # @abstractmethod
    def get_remove_torrents(self, config):
        """
        获取需要清理的种子清单
        :param config: 删种策略
        :return: 种子ID列表
        """
        pass

    # @abstractmethod
    def add_torrent(self, **kwargs):
        """
        添加下载任务
        """
        pass

    # @abstractmethod
    def start_torrents(self, ids):
        """
        下载控制：开始
        """
        pass

    # @abstractmethod
    def stop_torrents(self, ids):
        """
        下载控制：停止
        """
        pass

    # @abstractmethod
    def delete_torrents(self, delete_file, ids):
        """
        删除种子
        """
        pass

    # @abstractmethod
    def get_download_dirs(self):
        """
        获取下载目录清单
        """
        pass

    # @staticmethod
    def get_replace_path(path, downloaddir) -> (str, bool):
        """
        对目录路径进行转换
        :param path: 需要转换的路径
        :param downloaddir: 下载目录清单
        :return: 转换后的路径, 是否进行转换
        """
        if not path or not downloaddir:
            return "", False
        path = os.path.normpath(path)
        for attr in downloaddir:
            save_path = attr.get("save_path")
            if not save_path:
                continue
            save_path = os.path.normpath(save_path)
            container_path = attr.get("container_path")
            # 没有访问目录，视为与下载保存目录相同
            if not container_path:
                container_path = save_path
            else:
                container_path = os.path.normpath(container_path)
            if PathUtils.is_path_in_path(save_path, path):
                return path.replace(save_path, container_path), True
        return path, False

    # @abstractmethod
    def change_torrent(self, **kwargs):
        """
        修改种子状态
        """
        pass

    # @abstractmethod
    def get_downloading_progress(self):
        """
        获取下载进度
        """
        pass

    # @abstractmethod
    def set_speed_limit(self, **kwargs):
        """
        设置速度限制
        """
        pass

    # @abstractmethod
    def recheck_torrents(self, ids):
        """
        下载控制：重新校验
        """
        pass
