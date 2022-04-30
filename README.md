## 使用说明

现已更新docker webhook 版通知，可前往 https://github.com/Oscar1011/EasyXarr 配置使用

#### 下载仓库文件到本地或者使用以下命令：

    git clone https://github.com/Oscar1011/XarrNotifyScripts.git

#### Docker用户在 shell 终端按顺序执行以下命令安装环境

    # sonarr为容器名称，根据实际名称替换，radarr步骤相同
    docker exec -it sonarr /bin/bash  
    apt-get update
    apt-get install python3
    apt-get install python3-pip
    pip3 install requests
    pip3 install pyyaml

#### 群辉套件版用户确保安装的 python3套件 版本大于3.6，并安装依赖

    pip3 install requests
    pip3 install pyyaml

修改 config.yml 里面几个配置项，按说明修改即可

打开sonarr，在 settings -> connect 中添加一个 Custom Script。 运行文件选择 xarr_notify.sh 文件即可。\
打开radarr，在 设置 -> 通知连接 中添加一个 Custom Script。 运行文件选择 xarr_notify.sh 文件即可。

# 效果展示
![basic](https://gitee.com/oscar1011/raw/raw/master/20220225171813.png)

# 开源许可
本项目使用 [GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/) 作为开源许可证。

# 赞助支持
![basic](https://gitee.com/oscar1011/raw/raw/master/20220224162639.png)
