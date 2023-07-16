import py_opengauss
from fastapi import FastAPI, Response
from pydantic import BaseModel
from typing import Optional

app = FastAPI()
connects = {}

@app.get("/")
def read_root():
    return Response("Moon Crow") # 没错，这是我们的公司和产品名

class Connect(BaseModel):
    name: str
    database: str
    user: str
    password: str
    host: Optional[str] = "localhost"
    port: Optional[int] = 15400

@app.post("/connect")
def createConnect(connect: Connect):
    if connect.name in connects:
        return {"success": False, "message": "连接已存在"}
    try:
        db = py_opengauss.open(
            f"pq://{connect.user}:{connect.password}@{connect.host}:{connect.port}/{connect.database}")
        connects.update({connect.name: db})
        return {"success": True}
    except Exception as e:
        return Response(str(e))

# db = py_opengauss.open("pq://gauss:2023@gauss@127.0.0.1:15400/postgres")
# uvicorn main:app --host 192.168.227.131 --port 6677 --reload