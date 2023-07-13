# Datakit

openGauss + datakit 安装指南。

## 前言

这里，我们会用到 3 个用户，提前说一声，有个印象就好

- root: 大多数安装都用 root 权限
- omm: openGauss 最后一步安装（即 gs_preinstall 之后），以及 openGauss 的运行用户
- ops: datakit 的运行用户，只在最后运行的时候用一下，所有安装过程不用

## 配置 openEuler 开发环境

基于 **x86** 22.03 LTS SP1，SP2 应该差不多

ISO镜像：https://www.openeuler.org/zh/download/

或者你试一下直接用以下链接（可能不够快，那就要上面找一个）

https://repo.openeuler.openatom.cn/openEuler-22.03-LTS-SP2/ISO/x86_64/openEuler-22.03-LTS-SP2-x86_64-dvd.iso

### 系统安装

安装语言：**最好是英文！！**，脚本说的，我不知道中文行不行

为了省事，在选择软件源的时候一定要勾选以下这些

基本环境：~~服务器~~虚拟化主机

- 网络文件系统客户端
- Linux 的远程管理
- 开发工具（gcc）
- ~~openGauss 数据库~~（deprecated，版本不对，内置的太旧了）

> 如果你用英文，那稍微读一下找一下对应的3个打勾，以及，基本环境有3个也是要选的。

以及记得开 root 账户

### 配置 vscode ssh

以下得在虚拟机里面搞，比较费劲

需要修改一些东西，这里用 nano，没有的话 `yum install nano` 装一下

```
nano /etc/ssh/sshd_config
```

1. 
    原来
    ```
    #AllowAgentForwarding yes
    #AllowTcpForwarding yes
    #GatewayPorts  no
    ```

    改成

    ```
    AllowAgentForwarding yes
    AllowTcpForwarding yes
    GatewayPorts yes
    ```
2. 
    原来

    ```
    #PubkeyAuthentication yes
    ```

    改成

    ```
    PubkeyAuthentication yes
    ```
3. 
    原来

    ```
    #Banner none
    ```

    改成

    ```
    Banner none
    ```

4. 最后，重启

    ```
    systemctl restart sshd.service
    ```

> 如果你用 vm 虚拟机的话，ssh 的 IP 是第一个，192.168.227.xxx
>
> 如果你不喜欢用公钥，喜欢输密码，可以跳过第二步

### 安装 openGauss

#### 依赖

装一圈依赖

```
sudo yum install libaio-devel flex bison ncurses-devel glibc-devel patch readline-devel libnsl -y
```

> 还有一个 redhat-lsb-core 包找不到，似乎不影响，你可以试着装一下

-------

关防火墙

```
nano /etc/selinux/config
```

把 `SELINUX=enforcing` 改成 `SELINUX=disabled`

重启 `reboot`

继续关

```
systemctl disable firewalld.service
systemctl stop firewalld.service
```

-------

`nano /etc/profile`

添加一行

`export LANG=en_US.UTF-8`

----------

关闭RemoveIPC

1. 
    ```
    nano /etc/systemd/logind.conf
    ```

    取消下面这行的#注释

    ```
    #RemoveIPC=no
    ```
2. 
    ```
    nano /usr/lib/systemd/system/systemd-logind.service
    ```

    加一行

    ```
    RemoveIPC=no
    ```

3. 
    ```
    systemctl daemon-reload
    systemctl restart systemd-logind
    ```

### 其他准备

```
ln -s python3 /usr/bin/python
```

#### 安装

快捷下载

```
mkdir -p /opt/software/openGauss
cd /opt/software/openGauss
wget https://opengauss.obs.cn-south-1.myhuaweicloud.com/5.0.0/x86_openEuler_2203/openGauss-5.0.0-openEuler-64bit-all.tar.gz
tar -xvf openGauss-5.0.0-openEuler-64bit-all.tar.gz
```

后面官方的教程没有令人疑惑的地方了，所以请直接参考

https://docs.opengauss.org/zh/docs/5.0.0/docs/InstallationGuide/%E5%88%9B%E5%BB%BAXML%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6.html

其中，第一步写xml配置，直接抄示例里面的**单节点配置文件**，到 `/opt/software/openGauss/cluster_config.xml`

```
<?xml version="1.0" encoding="UTF-8"?>
<ROOT>
    <!-- openGauss整体信息 -->
    <CLUSTER>
        <!-- 数据库名称 -->
        <PARAM name="clusterName" value="dbCluster" />
        <!-- 数据库节点名称(hostname) -->
        <PARAM name="nodeNames" value="node1_hostname" />
        <!-- 数据库安装目录-->
        <PARAM name="gaussdbAppPath" value="/opt/huawei/install/app" />
        <!-- 日志目录-->
        <PARAM name="gaussdbLogPath" value="/var/log/omm" />
        <!-- 临时文件目录-->
        <PARAM name="tmpMppdbPath" value="/opt/huawei/tmp" />
        <!-- 数据库工具目录-->
        <PARAM name="gaussdbToolPath" value="/opt/huawei/install/om" />
        <!-- 数据库core文件目录-->
        <PARAM name="corePath" value="/opt/huawei/corefile" />
        <!-- 节点IP，与数据库节点名称列表一一对应 -->
        <PARAM name="backIp1s" value="192.168.0.1"/> 
    </CLUSTER>
    <!-- 每台服务器上的节点部署信息 -->
    <DEVICELIST>
        <!-- 节点1上的部署信息 -->
        <DEVICE sn="node1_hostname">
            <!-- 节点1的主机名称 -->
            <PARAM name="name" value="node1_hostname"/>
            <!-- 节点1所在的AZ及AZ优先级 -->
            <PARAM name="azName" value="AZ1"/>
            <PARAM name="azPriority" value="1"/>
            <!-- 节点1的IP，如果服务器只有一个网卡可用，将backIP1和sshIP1配置成同一个IP -->
            <PARAM name="backIp1" value="192.168.0.1"/>
            <PARAM name="sshIp1" value="192.168.0.1"/>
               
	    <!--dbnode-->
	    <PARAM name="dataNum" value="1"/>
	    <PARAM name="dataPortBase" value="15400"/>
	    <PARAM name="dataNode1" value="/opt/huawei/install/data/dn"/>
            <PARAM name="dataNode1_syncNum" value="0"/>
        </DEVICE>
    </DEVICELIST>
</ROOT>

```

**注意1** 其中的 `node1_hostname`，按照命令行里面 `hostname` 命令给出的结果填写

192.168.0.1 按照你 ssh 时候的 IP 填写

------ 

**注意2** 

初始化安装环境里：

7.使用gs_preinstall准备好安装环境。若为共用环境需加入--sep-env-file=ENVFILE参数分离环境变量，避免与其他用户相互影响，ENVFILE为用户自行指定的环境变量分离文件的路径，可以为一个空文件。

有很多种方式，选第一个，最傻瓜的：

采用交互模式执行前置，并在执行过程中自动创建操作系统root用户互信和omm用户互信：

------

注意3，安装完后，openGauss 默认运行在端口 15400 上

安装完后，在 omm 用户下，测试：

```
gs_om -t status
gsql -d postgres -p 15400
```

注意，`gsql -d postgres -p 15400` 就是以后连接数据库的命令，`postgres` 是数据库名，`15400` 是端口号

### 安装 Datakit

记得，安装 Datakit 时候，要用 root 用户

#### 安装依赖

官方仓库 dev 分支下面有脚本，但有点问题

见本仓库下我改过的最新脚本：

`install-depency.sh`

完事之后似乎有点问题，java 的环境变量还得手动配

写在 `/root/.bashrc` 里面

```
export JAVA_HOME=/etc/jdk11
export PATH=$JAVA_HOME/bin:$PATH
export CLASSPATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar
```

#### 准备jack用户

切换到 omm 用户（`su - omm`）

```
# 连接数据库（进入数据库的命令行）
gsql -d postgres -p 15400
# 创建用户（以下是在数据库命令行里面输入，从# 后面开始）
# 注意，密码xxxxx换成你自己的，以及记得，数据库里面要分号结尾
openGauss=# CREATE USER jack WITH MONADMIN password "xxxxxxxx";
openGauss=# alter user jack sysadmin;
# 以下是在系统命令行里面输入
[omm@test01 ~]$ gs_guc set -N all -I all -h "host all jack 192.168.1.0/24 sha256"
```

#### 安装datakit

记得切回 root 用户

```
wget https://opengauss.obs.cn-south-1.myhuaweicloud.com/latest/tools/Datakit/Datakit-5.0.0.tar.gz
mkdir -p /ops/server/openGauss-visualtool/logs /ops/server/openGauss-visualtool/config /ops/ssl /ops/files
tar -xvf Datakit-5.0.0.tar.gz -C /ops/server/openGauss-visualtool
cd /ops/server/openGauss-visualtool
cp application-temp.yml config/application-cus.yml
```

然后手动改 `config/application-cus.yml`

```
system:
  # File storage path
  defaultStoragePath: /ops/files
  # Whitelist control switch
  whitelist:
    enabled: false
server:
  port: 9494
  ssl:
    key-store: /ops/ssl/keystore.p12
    key-store-password: 123456
    key-store-type: PKCS12
    enabled: true
  servlet:
    context-path: /
logging:
  file:
    path: /ops/logs/
spring:
  datasource:
    type: com.alibaba.druid.pool.DruidDataSource
    driver-class-name: org.opengauss.Driver
    url: jdbc:opengauss://192.168.227.131:15400/postgres?currentSchema=public
    username: jack
    password: xxxxx
    druid:
      test-while-idle: false
      test-on-borrow: true
      validation-query: "select 1"
      validation-query-timeout: 10000
      connection-error-retry-attempts: 0
      break-after-acquire-failure: true
      max-wait: 3000
management:
  server:
    port: 9494
```

注意上面有个 password: xxxxx，填你刚刚创建jack的密码

还有一个 `192.168.227.131` 改成你 ssh 时候的 IP

收尾工作 + 创建一个ops用户，以及给ops用户权限

```
touch /ops/server/openGauss-visualtool/logs/visualtool-main.out
useradd -m ops
passwd ops
chown -R ops:ops /ops
```

#### 启动datakit

切换到 ops 用户

```
su - ops
```

测试一下 `java -version` 大概率是找不到命令，所以你要在 `/home/ops/.bashrc` 里面也加上

```
export JAVA_HOME=/etc/jdk11
export PATH=$JAVA_HOME/bin:$PATH
export CLASSPATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar
```

最后，执行需要用到用本仓库下的 `server.sh`，你可以把它放到 `/ops/server/openGauss-visualtool` 下面运行

`Usage: sh server.sh [start|stop|restart|status]`

运行输出在 `/ops/server/openGauss-visualtool/logs/visualtool-main.out`

一切顺利的话，访问 `https://ip:9494` 就可以看到登录界面了，管理员用户名 `admin`，密码 `admin123`