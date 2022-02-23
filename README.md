# 使用说明
1. 下载sonarr_notify.py 文件到本地，修改里面几个配置项，按说明修改即可。
2. 本人使用的是群辉套件版sonarr。 请确保环境上群辉中安装 python 3.6 以上版本。 Docker版需要在容器中安装。
   同时需要安装python3依赖， 安装python3 后运行 pip3 install requests 进行依赖安装
3. 将sonarr_notify.sh 和 sonarr_notify.py 脚本放置在同一目录下，.sh 文件中的路径请根据具体情况修改 （docker环境修改为docker中的py文件路径）
4. 打开sonarr，在 settings -> connect 中添加一个 Custom Script。 运行文件选择 .sh 文件即可。

# 效果展示
![basic](https://github.com/Oscar1011/XarrNotifyScripts/blob/main/raw/20220223174102.png)
