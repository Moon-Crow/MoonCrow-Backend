# Datakit

开发指南

## 配置 openEuler 开发环境

基于 22.03 LTS SP2

ISO镜像：https://www.openeuler.org/zh/download/

或者你试一下直接用以下链接（可能不够快，那就要上面找一个）

https://repo.openeuler.openatom.cn/openEuler-22.03-LTS-SP2/ISO/x86_64/openEuler-22.03-LTS-SP2-x86_64-dvd.iso

### 系统安装

ref: https://blog.csdn.net/weixin_42228815/article/details/129403406

为了省事，在选择软件源的时候一定要勾选以下这些

基本环境：服务器

- 网络文件系统客户端
- Linux 的远程管理
- 开发工具（gcc）
- openGauss 数据库

以及记得开 root 账户

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
....
AuthorizedKeyFile /root/.ssh/authorized_keys
```

然后把公钥传到 /root/.ssh/authorized_keys 里（新建文件夹+文件，公钥复制进去）

最后，记得重启ssh

```
systemctl restart sshd.service
```

> 如果你用 vm 虚拟机的话，ssh 的 IP 是第一个，192.168.227.xxx


### 安装 openGauss（deprecated）

```
groupadd dbgroup
useradd -g dbgroup omm
passwd omm
mkdir -p /opt/software/openGauss
tar -jxf openGauss-5.0.0-openEuler-64bit.tar.bz2 -C /opt/software/openGauss
chown -R omm /opt/software/openGauss
```

然后，先改一下 `PATH`

```
export PATH=/opt/software/openGauss/bin:$PATH
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

```
cd /opt/software/openGauss/simpleInstall
sh install.sh  -w xxxx # xxxx 为密码，中间问你要不要创建 demo 数据库，选是
```

检查是否安装成功

```
ps ux | grep gaussdb
gs_ctl query -D /opt/software/openGauss/data/single_node
```

### 安装 Datakit
#### 安装依赖

官方仓库 dev 分支下面有脚本，但有点问题

见本仓库下我改过的最新脚本：

`install-depency.sh`

### 安装datakit

