# Datakit

开发指南

## 配置 openEuler 开发环境

基于 **x86** 22.03 LTS SP1，SP2 应该差不多

ISO镜像：https://www.openeuler.org/zh/download/

或者你试一下直接用以下链接（可能不够快，那就要上面找一个）

https://repo.openeuler.openatom.cn/openEuler-22.03-LTS-SP2/ISO/x86_64/openEuler-22.03-LTS-SP2-x86_64-dvd.iso

### 系统安装

安装语言：**英文！！**

ref: https://blog.csdn.net/weixin_42228815/article/details/129403406

为了省事，在选择软件源的时候一定要勾选以下这些

基本环境：~~服务器~~虚拟化主机

- 网络文件系统客户端
- Linux 的远程管理
- 开发工具（gcc）
- ~~openGauss 数据库~~（deprecated，版本不对，内置的太旧了）

以及记得开 root 账户

打开后先 `yum update` 一下

### 配置 vscode ssh

需要修改一些东西，这里用 nano，没有的话 `sudo yum install nano` 装一下

```
nano /etc/ssh/sshd_config
```

找到这三行，比如你搜（ctrl+W）一下

```
#AllowAgentForwarding yes
#AllowTcpForwarding yes
#GatewayPorts  no
```

改成（取消注释+改）

```
AllowAgentForwarding yes
AllowTcpForwarding yes
GatewayPorts yes
```

如果你喜欢公钥登录，找到对应的地方改成下面这样，比如你搜（ctrl+W）`authorized_keys` 就能找到我说的在哪

```
PubkeyAuthentication yes
```

然后把公钥传到 /root/.ssh/authorized_keys 里（新建文件夹+文件，公钥复制进去）

最后，记得重启ssh

```
systemctl restart sshd.service
```

> 如果你用 vm 虚拟机的话，ssh 的 IP 是第一个，192.168.227.xxx


### 安装 openGauss

#### 依赖

装一圈依赖

```
sudo yum install libaio-devel flex bison ncurses-devel glibc-devel patch readline-devel libnsl -y
```

> 还有一个 redhat-lsb-core 包找不到，似乎不影响

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

`nano /etc/profile`

`export LANG=en_US.UTF-8`

#### 安装（未完成）

> 建议在 root 下把 datakit 的依赖也安装完再回来。

```
mkdir -p /opt/software/openGauss
wget https://opengauss.obs.cn-south-1.myhuaweicloud.com/5.0.0/x86_openEuler_2203/openGauss-5.0.0-openEuler-64bit-all.tar.gz
tar -xvf openGauss-5.0.0-openEuler-64bit-all.tar.gz
```

重进服务器，以 omm 账户登录，或者 `su - omm` 切换

> 比如，你可以这样配置 vscode ssh
> 
> ```
> Host openEuler_omm
>  HostName 192.168.227.131
>  User omm
> 
> Host openEuler_root
>   HostName 192.168.227.131
>   User root
> ```

现在，你已经以 omm 登录

未完待续

> 注意，此时，openGauss 默认运行在端口 5432 上

### 安装 Datakit
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

### 安装datakit

```
wget https://opengauss.obs.cn-south-1.myhuaweicloud.com/latest/tools/Datakit/Datakit-5.0.0.tar.gz
mkdir -p /ops/server/openGauss-visualtool/logs /ops/server/openGauss-visualtool/config /ops/ssl /ops/files
useradd -m ops
tar -xvf Datakit-5.0.0.tar.gz -C /ops/server/openGauss-visualtool
cd /ops/server/openGauss-visualtool
cp application-temp.yml config/application-cus.yml
```

然后手动改 `application-cus.yml`

