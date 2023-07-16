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
    show()
    demo()
    model()
    
if __name__ == "__main__":
    test()
    
# gsql -d postgres -p 15400 -U gauss -W 2023@gauss