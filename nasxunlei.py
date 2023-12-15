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

__xunlei_get_token_js = """
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

%__FROM_XUNLEI_WEB_IU__%

"""