## 数据库准备

### 数据库启动

```shell
su - omm
gs_om -t start
```

### 创建用户

先创建名为 gauss 密码为 2023@gauss 的用户，并测试登录，如果你不知道怎么操作，参考：

'''
shell
[omm@bogon ~]$ gsql -d postgres -p 15400
gsql ((openGauss 5.0.0 build a07d57c3) compiled at 2023-03-29 03:37:13 commit 0 last mr  )
Non-SSL connection (SSL connection is recommended when requiring high-security)
Type "help" for help.

openGauss=#     create user gauss with password "2023@gauss";
openGauss=#     \q
[omm@bogon ~]$ gsql -d postgres -p 15400 -U gauss -W 2023@gauss
gsql ((openGauss 5.0.0 build a07d57c3) compiled at 2023-03-29 03:37:13 commit 0 last mr  )
Non-SSL connection (SSL connection is recommended when requiring high-security)
Type "help" for help.

openGauss=>     \q
'''

## 服务器准备

### 安装 python 依赖

```shell
pip install py_opengauss fastapi uvicorn[standard] numpy pandas matplotlib scipy scikit-learn
```

你可以忽略 root 警告

### 申请证书

```shell
yum install openssl
cd backend/
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout server.key -out server.crt
```

注意，你可能会遇到和 .so 有关的错误，这是由于 openGauss 在安装时破坏了一些环境变量，你可以通过以下命令修复：

```shell
export LD_LIBRARY_PATH=/usr/lib64:$LD_LIBRARY_PATH
```

> 一般地，你可以用 `find / -name *.so` 查找文件，如果找到了，就可以类似上面手动添加路径，更多时候，这个问题是因为缺了软件的动态库，但这里是 openGauss 把系统的动态库干掉了。

### 修改配置文件

```yaml
host: "192.168.227.131"
ssl_certfile: "server.crt"
ssl_keyfile: "server.key"
```

注意修改虚拟机IP，证书和密钥的路径（如果你在 `/backend` 下输入申请证书节的指令，那么这里就不用修改了）

## 启动

```shell
python run.py --https
```

或

```shell
python run.py
```

## Update

2023-7-18: 更新了服务器启动脚本，增加了配置文件 `config.yaml`，支持 https 启动。增加了更多模型以及数据集。

2023-9-19: 更新了chatGPT功能，为了安全，api_key从系统环境变量中获取，key找潘俊达要，之前的已经失效。

```shell
export OPENAI_API_KEY=your_key
```
