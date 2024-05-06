# NAS 迅雷下载器 for NasTools

## 前言

此仓库与 nas-tools 原作者以及其他任何 nas-tools 及其插件等衍生作品的维护者无关，您不应该请求他们为此仓库做任何适配工作。

您不应该使用迅雷下载任何 PT 资源，因您使用迅雷下载 PT 资源而造成的任何损失与此仓库及其作者无关，同时介于迅雷的行径，也不建议用作下载任何 BT 资源。

您不应该在任何场合公开宣传此项目，尤其是与 nas-tools 原项目作者及其所有相关维护者、贡献者相关的场所，若此项目受到不必要的过多关注或舆论，将立即删除，请低调使用。

## 介绍

这是一个适用于 nas-tools 的迅雷下载器实现，需要您自行部署 NAS 迅雷。

项目使用且修改了 [opennaslab/kubespider - A global resource download orchestration system, build your home download center.](https://github.com/opennaslab/kubespider) 的部分源码，感谢大佬的辛勤付出。

### 食用方法

1. 使用 `git clone https://github.com/sgpublic/xunlei-nastools --recursive` 克隆本项目。
2. 将本项目 `third_party` 目录映射到 nas-tools 容器的 `/nas-tools/third_party_nas_xunlei`。
3. 将本项目 `nasxunlei.py` 文件映射到 nas-tools 容器的 `/nas-tools/app/downloader/client/nasxunlei.py`。
4. 重启 nas-tools，enjoy！

### 未来适配

#### 1.18.0 及以下

若提示签名失效，您可根据 [迅雷下载提供器安装和配置](https://github.com/opennaslab/kubespider/tree/f55eab6a931d1851d5cbe2b6467d7dde96bffdef/docs/zh/user_guide/thunder_install_config) 创建 `get_token.js` 文件，改名为 `xunlei_get_token.js` 并放入 nas-tools 配置文件夹中（与 `config.yaml` 同一目录），然后重启 nas-tools 即可。

#### 1.21.1 及以上

1.21.1 版本及以上 xunlei 直接生成一个 `pan_auth` 放到 html 里了，理论上不再需要操作 `get_token.js`，有效期待测试。

#### 其余版本

其余版本待测试，但本仓库优先适配最新版本，必要情况下将放弃旧版本适配