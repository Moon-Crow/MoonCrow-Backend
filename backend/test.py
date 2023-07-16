from requests import post
import json

def request(api, data, host="192.168.227.131", port="6677"):
    return post(f"http://{host}:{port}{api}", data=json.dumps(data))

def connect():
    print("connect")
    data = {
        "name": "test",
        "database": "postgres",
        "user": "gauss",
        "password": "2023@gauss"
    }
    req = request("/connect", data)
    print(req.json())
    
def show():
    print("show")
    data = {
        "name": "test",
        "table": "test"
    }
    req = request("/show", data)
    print(req.json())

def demo():
    print("demo")
    data = {
        "name": "test",
        "table": "titanic",
        "dataset": "titanic"
    }
    req = request("/demo", data)
    print(req.json())

def test():
    connect()
    show()
    demo()
    
if __name__ == "__main__":
    test()
    
# gsql -d postgres -p 15400 -U gauss -W 2023@gauss