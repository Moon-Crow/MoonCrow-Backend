import py_opengauss
from sqlalchemy import create_engine
from fastapi import FastAPI, Response
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import os.path as osp

app = FastAPI()
connects = {}
debug = True

@app.get("/")
def read_root():
    return Response("Moon Crow") # 没错，这是我们的公司和产品名

class NewConnect(BaseModel):
    name: str
    database: str
    user: str
    password: str
    host: Optional[str] = "127.0.0.1"
    port: Optional[int] = 15400

def generateConnectUrl(connect: NewConnect):
    return f"pq://{connect.user}:{connect.password}@{connect.host}:{connect.port}/{connect.database}"

@app.post("/connect")
def createConnect(connect: NewConnect):
    try:
        if connect.name in connects:
            raise Exception("连接已存在")
        db = py_opengauss.open(generateConnectUrl(connect))
        connects.update({connect.name: [db, connect]})
        return {"success": True}
    except Exception as e:
        return {"success": False, "message": str(e)}
    
class Demo(BaseModel):
    name: str
    table: str
    dataset: str

DATASET = ["titanic"]

def to_gauss(df, table, db):
    # TODO
    pass

@app.post("/demo")
def createDemoTable(demo: Demo):
    try:
        if demo.dataset not in DATASET:
            raise Exception("数据集不存在")
        db, connect = connects[demo.name]
        if db is None:
            raise Exception("连接不存在")
        df = pd.read_csv(osp.join("demo", f"{demo.dataset}.csv"))
        to_gauss(df, demo.table, db)
        return {"success": True}
    except Exception as e:
        return {"success": False, "message": str(e)}

class Show(BaseModel):
    name: str
    table: str

@app.post("/show")
def show(connect: Show):
    try:
        db, _ = connects[connect.name]
        result = db.prepare(f"SELECT tablename FROM pg_tables WHERE SCHEMANAME = 'public' AND CREATED >= '2023-07-15';")
        table_name = result()
        columns = []
        for d in table_name:
            column = [] # TODO
            columns.append(column)
        return {"success": True, "data": list(zip(table_name, columns))}
    except Exception as e:
        return {"success": False, "message": str(e)}

def main():
    if debug:
        con = NewConnect(name="debug", database="postgres", user="gauss", password="2023@gauss")
        db = py_opengauss.open(generateConnectUrl(con))
        connects.update({con.name: [db, con]})

main()
# uvicorn main:app --host 192.168.227.131 --port 6677 --reload
# ln -s /opt/software/openGauss/libcgroup/lib/* /usr/lib/
# ln -s /opt/software/openGauss/libcgroup/lib/* /usr/lib64/