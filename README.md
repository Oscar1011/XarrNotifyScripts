# 使用说明
1. 下载xarr_notify.py, xarr_notify.sh, config.yml 文件到本地，修改 config.yml 里面几个配置项，按说明修改即可。
2. 本人使用的是群辉套件版sonarr/radarr。 请确保环境上群辉中安装 python 3.6 以上版本。 Docker版需要在容器中安装。
   同时需要安装python3依赖， 安装python3 后运行 pip3 install requests 进行依赖安装
3. 将脚本和配置文件放置在同一目录下
4. 打开sonarr，在 settings -> connect 中添加一个 Custom Script。 运行文件选择 xarr_notify.sh 文件即可。
   打开radarr，在 设置 -> 通知连接 中添加一个 Custom Script。 运行文件选择 xarr_notify.sh 文件即可。
   
python3 环境安装可以看仔老师的教程 https://post.smzdm.com/p/az324xxn

# 效果展示
![basic](https://gitee.com/oscar1011/raw/raw/master/20220225171813.png)

# 赞助支持
![basic](https://gitee.com/oscar1011/raw/raw/master/20220224162639.png)
