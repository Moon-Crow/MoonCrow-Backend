import py_opengauss
from fastapi import FastAPI, Response
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import os.path as osp
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

app = FastAPI()
connects = {}
debug = True

@app.get("/")
def read_root():
    return Response("Moon Crow") # 没错，这是我们的公司和产品名

class NewConnect(BaseModel):
    connName: str
    database: str
    user: str
    password: str
    host: Optional[str] = "127.0.0.1"
    port: Optional[int] = 15400

def generateConnectUrl(connect: NewConnect):
    return f"pq://{connect.user}:{connect.password}@{connect.host}:{connect.port}/{connect.database}"

class NormalResponse(BaseModel):
    success: bool
    message: Optional[str] = None

@app.post("/connect")
def createConnect(connect: NewConnect)->NormalResponse:
    try:
        if connect.connName in connects:
            raise Exception("连接已存在")
        db = py_opengauss.open(generateConnectUrl(connect))
        connects.update({connect.connName: [db, connect]})
        return NormalResponse(success=True)
    except Exception as e:
        return NormalResponse(success=False, message=str(e))
    
class Demo(BaseModel):
    connName: str
    table: str
    dataset: str

DATASET = ["titanic"]

def to_gauss(df:pd.DataFrame, table, db, connect:NewConnect):
    db.execute(f"DROP TABLE IF EXISTS {table};")
    column_names = df.columns
    column_types = df.dtypes.values
    def mapper(dt):
        if np.dtype(dt).name == "object":
            return "text"
        else:
            return "numeric"
    column_types = list(map(mapper, column_types))
    columns = ",".join([f"{n} {t}" for n,t in zip(column_names, column_types)])
    db.execute(f"CREATE TABLE {table} ({columns})")
    ins = db.prepare(f"INSERT INTO {table} VALUES ({','.join(['$'+str(i+1) for i in range(len(column_names))])})")
    df.replace(np.nan, None, inplace=True)
    for row in df.values:
        ins(*row)
    pass

@app.post("/demo")
def createDemoTable(demo: Demo) -> NormalResponse:
    try:
        if demo.dataset not in DATASET:
            raise Exception("数据集不存在")
        db, connect = connects[demo.connName]
        if db is None:
            raise Exception("连接不存在")
        path = osp.join("demo", f"{demo.dataset}.csv")
        df = pd.read_csv(path)
        to_gauss(df, demo.table, db, connect)
        # db.execute(f"COPY {demo.table} FROM '{path}' WITH DELIMITER ',' CSV HEADER;")
        return NormalResponse(success=True)
    except Exception as e:
        return NormalResponse(success=False, message=str(e))

class Show(BaseModel):
    connName: str

class ShowResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[list] = [["tableName1", ["col11", "col12"]], ["tableName2", ["col21", "col22"]]]

@app.post("/show", description="显示数据库中的表，和对应的列，该函数未完成，openGauss 不知道怎么获得列信息")
def show(connect: Show) -> ShowResponse:
    try:
        db, _ = connects[connect.connName]
        result = db.prepare(f"SELECT tablename FROM pg_tables WHERE SCHEMANAME = 'public' AND CREATED >= '2023-07-15';")
        table_name = result()
        columns = []
        for d in table_name:
            column = [] # TODO
            columns.append(column)
        return ShowResponse(success=True, data=list(zip(table_name, columns)))
    except Exception as e:
        return ShowResponse(success=False, message=str(e), data=None)

class Model(BaseModel):
    connName: str = "test"
    table: str = "titanic"
    model: str = "linear"
    columns: list = ["Age","Pclass", "Survived"]
    modelParams: Optional[dict] = {}
    dropna: Optional[bool] = True

class ModelResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = {"Age":[0, 1], "Pclass":[0, 1], "Survived":[0, 1],
                            "predAge":[0, 1], "predPclass":[0, 1], "predSurvived":[0, 1]}

def decimal2float(cols):
    return [list(map(float, col)) for col in cols]

def select_from(db, columns, table, dropna=True, sample_size=10000):
    prep = db.prepare(f"SELECT {','.join(columns)} FROM {table};")
    rows = prep()
    if dropna:
        df = pd.DataFrame(rows, columns=columns)
        df = df.dropna()
        rows = df.values
    if len(rows)>sample_size:
        rows = np.random.choice(rows, sample_size, replace=False)
    cols = [list(col) for col in np.array(rows).T]
    return cols

modelAPIDesc = '''
目前实现的模型有：

select：从 table 中选择 columns 列的数据

linear: 从 table 中选择 columns[:-1] 列作为自变量，columns[-1] 列作为因变量，进行线性回归

cluster: 从 table 中选择 columns 列作为数据，进行聚类，聚类方法为 KMeans，聚类数目为 modelParams["k"]

当 model = cluster 时，需要传入 modelParams = {"k": 3}，否则 modelParams 可为空
'''

@app.post("/model", description=modelAPIDesc)
def createModel(model_config:Model)->ModelResponse:
    try:
        db,_ = connects[model_config.connName]
        if model_config.model=="select":
            ori_data = select_from(db, model_config.columns, model_config.table, model_config.dropna)
            data = dict(zip(model_config.columns, ori_data))
        elif model_config.model=="linear":
            ori_data = select_from(db, model_config.columns, model_config.table, model_config.dropna)
            ori_data = decimal2float(ori_data) # 必须全是数字
            length = len(ori_data[0])
            if length**len(ori_data[:-1])>100000:
                length = int(length**(1/len(ori_data[:-1])))
            model = LinearRegression()
            model.fit(np.array(ori_data[:-1]).T, np.array(ori_data[-1]).T)
            pred_xs = np.meshgrid(*[np.linspace(min(ori_d),max(ori_d),length) for ori_d in ori_data[:-1]])
            pred_xs = [pred_x.flatten() for pred_x in pred_xs]
            pred_y = model.predict(np.array(pred_xs).T)
            columns = model_config.columns
            columns = columns + ["pred" + col for col in columns]
            pred_xs = [pred_x.tolist() for pred_x in pred_xs]
            data = dict(zip(columns, ori_data + pred_xs + [pred_y.tolist()]))
        elif model_config.model=="cluster":
            k = model_config.modelParams["k"]
            ori_data = select_from(db, model_config.columns, model_config.table, model_config.dropna)
            ori_data = decimal2float(ori_data) # 必须全是数字
            length = len(ori_data[0])
            if length**len(ori_data)>100000:
                length = int(length**(1/len(ori_data)))
            model = KMeans(n_clusters=k)
            model.fit(np.array(ori_data).T)
            pred_xs = np.meshgrid(*[np.linspace(min(ori_d),max(ori_d),length) for ori_d in ori_data])
            pred_xs = [pred_x.flatten() for pred_x in pred_xs]
            pred_y = model.predict(np.array(pred_xs).T)
            columns = model_config.columns
            columns = columns + ["pred" + col for col in columns] + ["pred"]
            pred_xs = [pred_x.tolist() for pred_x in pred_xs]
            data = dict(zip(columns, ori_data + pred_xs + [pred_y.tolist()]))
        return ModelResponse(success=True, data=data)
    except Exception as e:
        return ModelResponse(success=False, message=str(e), data=None)
    

def main():
    if debug:
        con = NewConnect(connName="debug", database="postgres", user="gauss", password="2023@gauss")
        db = py_opengauss.open(generateConnectUrl(con))
        connects.update({con.connName: [db, con]})

main()
# uvicorn main:app --host 192.168.227.131 --port 6677 --reload
# ln -s /opt/software/openGauss/libcgroup/lib/* /usr/lib/
# ln -s /opt/software/openGauss/libcgroup/lib/* /usr/lib64/