# NAS 迅雷下载器 for NasTools

## 前言

此仓库与 nas-tools 原作者以及其他任何 nas-tools 及其插件等衍生作品的维护者无关，您不应该请求他们为此仓库做任何适配工作。

您不应该使用迅雷下载任何 PT 资源，因您使用迅雷下载 PT 资源而造成的任何损失与此仓库及其作者无关，同时介于迅雷的行径，也不建议用作下载任何 BT 资源。

## 介绍

这是一个适用于 nas-tools 的迅雷下载器实现，需要您自行部署 NAS 迅雷。

### 食用方法

1. 将本项目 `third_party` 目录映射到 nas-tools 容器的 `/nas-tools/third_party_nas_xunlei`。
2. 将本项目 `nasxunlei.py` 文件映射到 nas-tools 容器的 `/nas-tools/app/downloader/client/nasxunlei.py`。
3. 重启 nas-tools，enjoy！
