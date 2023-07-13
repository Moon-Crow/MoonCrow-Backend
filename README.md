# Datakit

开发指南

## 配置 openEuler 开发环境

基于 22.03 LTS SP2

ISO镜像：https://www.openeuler.org/zh/download/

### 系统安装

ref: https://blog.csdn.net/weixin_42228815/article/details/129403406

为了省事，在选择软件源的时候一定要勾选以下这些

基本环境：虚拟化主机

- 网络文件系统客户端
- Linux 的远程管理
- 开发工具（gcc）

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
