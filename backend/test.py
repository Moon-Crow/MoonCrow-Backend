# 请先创建名为 gauss 密码为 2023@gauss 的用户，并测试登录，如果你不知道怎么操作，参考：

'''
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

# 但其实不推荐这样测试，https:IP:6677/docs 提供了交互式的测试界面

from requests import post
import json

HOST = "192.168.227.131"

def request(api, data, host=HOST, port="6677"):
    return post(f"http://{host}:{port}{api}", data=json.dumps(data))

def connect():
    print("connect")
    data = {
        "connName": "test",
        "database": "postgres",
        "user": "gauss",
        "password": "2023@gauss"
    }
    req = request("/connect", data)
    print(req.json())
    
def show():
    print("show")
    data = {
        "connName": "test",
        "table": "test"
    }
    req = request("/show", data)
    print(req.json())

def demo():
    print("demo")
    data = {
        "connName": "test",
        "table": "titanic",
        "dataset": "titanic"
    }
    req = request("/demo", data)
    print(req.json())

def model(model="cluster"):
    print("model")
    data= {
        "connName": "test",
        "table": "titanic",
        "model": model,
        "columns": ["Age","Pclass", "Survived"]
    }
    if model=="cluster":
        data.update({"modelParams": {"k": 3}})
    req = request("/model", data)
    print(req.json())

def test():
    connect()
    demo()
    show()
    model()
    
if __name__ == "__main__":
    test()