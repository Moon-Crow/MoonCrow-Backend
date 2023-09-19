import py_opengauss
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import os
import os.path as osp
import numpy as np
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from sklearn.cluster import MiniBatchKMeans
import yaml
import openai
import json

openai.api_key = os.environ.get("OPENAI_API_KEY")
config = yaml.load(open("config.yaml", "r"), Loader=yaml.FullLoader)
host = config["host"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

connects = {}
debug = False


@app.get("/")
def read_root():
    return Response("Moon Crow")  # 没错，这是我们的公司和产品名


class NewConnect(BaseModel):
    connName: str = "test"
    database: str = "postgres"
    user: str = "gauss"
    password: str = "2023@gauss"
    host: Optional[str] = host
    port: Optional[int] = 15400


def generateConnectUrl(connect: NewConnect):
    return f"pq://{connect.user}:{connect.password}@{connect.host}:{connect.port}/{connect.database}"


class NormalResponse(BaseModel):
    success: bool
    message: Optional[str] = None


@app.post("/connect")
def createConnect(connect: NewConnect) -> NormalResponse:
    try:
        if connect.connName in connects:
            raise Exception("连接已存在")
        db = py_opengauss.open(generateConnectUrl(connect))
        connects.update({connect.connName: [db, connect]})
        return NormalResponse(success=True)
    except Exception as e:
        return NormalResponse(success=False, message=str(e))


class Chat(BaseModel):
    connName: str = "test"
    content: str = "生成titanic表上，Survived列和Age以及Pclass的关系"


class ChatResponse(BaseModel):
    success: str = "success"
    function_call: dict


functions = [
    {
        "name": "model",
        "description": "为数据库表上的指定列选择机器学习模型并建模",
        "parameters": {
            "type": "object",
            "properties": {
                "table": {
                    "type": "string",
                    "description": "要查询的表",
                },
                "model": {
                    "type": "string",
                    "enum": ["logistic", "svm", "kmeans"],
                    "description": "要使用的机器学习模型，默认相关关系使用svm，分布使用kmeans",
                },
                "columns": {
                    "type": "array",
                    "description": "要查询的列，如果model是预测任务则输出数组的最后一个元素表示因变量，前面的表示自变量，例如询问y和a以及b的关系，则y是因变量，需要在输出数组的最后一个位置",
                    "items": {"type": "string", "description": "列名"},
                },
            },
            "required": ["table", "model", "columns"],
        },
    }
]


@app.post("/chat")
def chat(c: Chat):
    try:
        messages = [
            # {"role": "system", "content": ""},
            {"role": "user", "content": c.content},
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613", messages=messages, functions=functions
        )
        print(response)
        function_call = response["choices"][0]["message"]["function_call"]
        function_call["arguments"] = json.loads(function_call["arguments"])
        return ChatResponse(success=True, function_call=function_call)
    except Exception as e:
        return NormalResponse(success=False, message=str(e))


class Demo(BaseModel):
    connName: str = "test"
    table: Optional[str] = "boston"
    dataset: str = "boston"


def to_gauss(df: pd.DataFrame, table, db, connect: NewConnect):
    db.execute(f"DROP TABLE IF EXISTS {table};")
    column_names = df.columns
    column_types = df.dtypes.values

    def mapper(dt):
        if np.dtype(dt).name == "object":
            return "text"
        else:
            return "numeric"

    column_types = list(map(mapper, column_types))
    columns = ",".join([f"{n} {t}" for n, t in zip(column_names, column_types)])
    db.execute(f"CREATE TABLE {table} ({columns})")
    ins = db.prepare(
        f"INSERT INTO {table} VALUES ({','.join(['$'+str(i+1) for i in range(len(column_names))])})"
    )
    df.replace(np.nan, None, inplace=True)
    for row in df.values:
        ins(*row)
    pass


@app.post("/demo")
def createDemoTable(demo: Demo) -> NormalResponse:
    try:
        if connects.get(demo.connName) is None:
            raise Exception("连接不存在")
        folder_path = "./demo"
        files = os.listdir(folder_path)
        datasets = list(filter(lambda x: x.endswith(".csv"), files))
        datasets = list(map(lambda x: x[:-4], datasets))
        if demo.dataset not in datasets:
            raise Exception("数据集不存在，目前支持的数据集有：" + ",".join(datasets))
        db, connect = connects[demo.connName]
        if db is None:
            raise Exception("连接不存在")
        path = osp.join("demo", f"{demo.dataset}.csv")
        df = pd.read_csv(path)
        if demo.table is None:
            demo.table = demo.dataset
        to_gauss(df, demo.table, db, connect)
        lines = db.prepare(f"SELECT COUNT(*) AS row_count FROM {demo.table};")()
        return NormalResponse(success=True, message=f"创建成功，数据库返回 {lines[0][0]} 条数据")
    except Exception as e:
        return NormalResponse(success=False, message=str(e))


class Show(BaseModel):
    connName: str = "test"


class ShowResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[list] = [
        {
            "tableName": "titanic",
            "columns": [
                {"name": "PassengerId", "type": "numeric"},
                {"name": "Name", "type": "text"},
            ],
        },
        {"tableName": "test", "columns": [{"name": "col", "type": "numeric"}]},
    ]


@app.post("/show", description="显示数据库中的表，和对应的列及类型，现阶段，可以假设类型只有 str 和 numeric 两种。")
def show(connect: Show) -> ShowResponse:
    try:
        if connects.get(connect.connName) is None:
            raise Exception("连接不存在")
        db, conn = connects[connect.connName]
        result = db.prepare(
            f"SELECT tablename FROM pg_tables WHERE SCHEMANAME = '{conn.user}';"
        )
        table_name = result()
        table_name = [t[0] for t in table_name]
        columns = []
        get_col = db.prepare(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = $1;"
        )
        data = []
        for d in table_name:
            column = get_col(f"{d}")
            columns.append(column)
            data.append(
                {
                    "tableName": d,
                    "columns": [{"name": c[0], "type": c[1]} for c in column],
                }
            )
        return ShowResponse(success=True, data=data)
    except Exception as e:
        return ShowResponse(success=False, message=str(e), data=None)


class Model(BaseModel):
    connName: str = "test"
    table: str = "boston"
    model: str = "svm"
    columns: list = ["LSTAT", "RM", "MEDV"]
    reduce: Optional[bool] = False
    modelParams: Optional[dict] = {}
    limit: Optional[int] = 3000
    dropna: Optional[bool] = True


class ModelResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = {
        "Age": [0, 1],
        "Pclass": [0, 1],
        "Survived": [0, 1],
        "predAge": [0, 1],
        "predPclass": [0, 1],
        "predSurvived": [0, 1],
    }


def decimal2float(cols):
    return [list(map(float, col)) for col in cols]


def select_from(db, columns, table, dropna=True, sample_size=10000):
    prep = db.prepare(f"SELECT {','.join(columns)} FROM {table};")
    rows = prep()
    if dropna:
        df = pd.DataFrame(rows, columns=columns)
        df = df.dropna()
        rows = df.values
    if len(rows) > sample_size:
        rows = np.random.choice(rows, sample_size, replace=False)
    cols = [list(col) for col in np.array(rows).T]
    return cols


modelAPIDesc = """

输出的数据格式为：

select 出来的原数据，和为了预测生成的测试点，其列名前加上 pred

目前实现的模型有：

select: 从 table 中选择 columns 列的数据

linear: 从 table 中选择 columns[:-1] 列作为自变量，columns[-1] 列作为因变量，进行线性回归

logistic: 从 table 中选择 columns[:-1] 列作为自变量，columns[-1] 列作为因变量，进行逻辑回归

kmeans: 从 table 中选择 columns 列作为数据，进行聚类，聚类方法为 KMeans，聚类数目为 modelParams["k"]，最后的输出会多两列

MiniBatchKMeans: 从 table 中选择 columns 列作为数据，进行聚类，聚类方法为 MiniBatchKMeans，聚类数目为 modelParams["k"]，最后的输出会多两列

分别是 Label 和 predLabel 表示原始数据上的聚类结果和生成的测试点的聚类结果

注意，当 model = cluster 时，需要传入 modelParams = {"k": 3}，指定聚类的类数（最好是设成一个用户指定的参数）否则 modelParams 可为空
"""


@app.post("/model", description=modelAPIDesc)
def createModel(model_config: Model) -> ModelResponse:
    try:
        if connects.get(model_config.connName) is None:
            raise Exception("连接不存在")
        db, _ = connects[model_config.connName]
        if model_config.model == "select":
            ori_data = select_from(
                db, model_config.columns, model_config.table, model_config.dropna
            )
            data = dict(zip(model_config.columns, ori_data))
        elif model_config.model == "linear":  # linear model
            ori_data = select_from(
                db,
                model_config.columns,
                model_config.table,
                model_config.dropna,
                model_config.limit,
            )
            ori_data = decimal2float(ori_data)  # 必须全是数字
            length = int(model_config.limit ** (1 / len(ori_data[:-1])))
            model = LinearRegression()
            model.fit(np.array(ori_data[:-1]).T, np.array(ori_data[-1]).T)
            pred_xs = np.meshgrid(
                *[
                    np.linspace(min(ori_d), max(ori_d), length)
                    for ori_d in ori_data[:-1]
                ]
            )
            pred_xs = [pred_x.flatten() for pred_x in pred_xs]
            pred_y = model.predict(np.array(pred_xs).T)
            columns = model_config.columns
            columns = columns + ["pred" + col for col in columns]
            pred_xs = [pred_x.tolist() for pred_x in pred_xs]
            data = dict(zip(columns, ori_data + pred_xs + [pred_y.tolist()]))
        elif model_config.model == "logistic":  # logistic model
            ori_data = select_from(
                db,
                model_config.columns,
                model_config.table,
                model_config.dropna,
                model_config.limit,
            )
            ori_data = decimal2float(ori_data)  # 必须全是数字
            length = int(model_config.limit ** (1 / len(ori_data[:-1])))
            model = LogisticRegression()
            model.fit(np.array(ori_data[:-1]).T, np.array(ori_data[-1]).T)
            pred_xs = np.meshgrid(
                *[
                    np.linspace(min(ori_d), max(ori_d), length)
                    for ori_d in ori_data[:-1]
                ]
            )
            pred_xs = [pred_x.flatten() for pred_x in pred_xs]
            pred_y = model.predict(np.array(pred_xs).T)
            columns = model_config.columns
            columns = columns + ["pred" + col for col in columns]
            pred_xs = [pred_x.tolist() for pred_x in pred_xs]
            data = dict(zip(columns, ori_data + pred_xs + [pred_y.tolist()]))
        elif model_config.model == "kmeans":  # kmeans cluster model
            k = model_config.modelParams["k"]
            ori_data = select_from(
                db,
                model_config.columns,
                model_config.table,
                model_config.dropna,
                model_config.limit,
            )
            ori_data = decimal2float(ori_data)  # 必须全是数字
            length = int(model_config.limit ** (1 / len(ori_data)))
            model = KMeans(n_clusters=k)
            model.fit(np.array(ori_data).T)
            pred_xs = np.meshgrid(
                *[np.linspace(min(ori_d), max(ori_d), length) for ori_d in ori_data]
            )
            pred_xs = [pred_x.flatten() for pred_x in pred_xs]
            pred_y = model.predict(np.array(pred_xs).T)
            columns = model_config.columns
            columns.append("Label")
            columns = columns + ["pred" + col for col in columns]
            pred_xs = [pred_x.tolist() for pred_x in pred_xs]
            data = dict(
                zip(
                    columns,
                    ori_data + [model.labels_.tolist()] + pred_xs + [pred_y.tolist()],
                )
            )
        elif model_config.model == "MiniBatchKMeans":  # MiniBatchKMeans cluster model
            k = model_config.modelParams["k"]
            ori_data = select_from(
                db,
                model_config.columns,
                model_config.table,
                model_config.dropna,
                model_config.limit,
            )
            ori_data = decimal2float(ori_data)  # 必须全是数字
            length = int(model_config.limit ** (1 / len(ori_data)))
            model = MiniBatchKMeans(
                n_clusters=k,
                init="k-means++",
                max_no_improvement=10,
                batch_size=30,
                random_state=28,
            )
            model.fit(np.array(ori_data).T)
            pred_xs = np.meshgrid(
                *[np.linspace(min(ori_d), max(ori_d), length) for ori_d in ori_data]
            )
            pred_xs = [pred_x.flatten() for pred_x in pred_xs]
            pred_y = model.predict(np.array(pred_xs).T)
            columns = model_config.columns
            columns.append("Label")
            columns = columns + ["pred" + col for col in columns]
            pred_xs = [pred_x.tolist() for pred_x in pred_xs]
            data = dict(
                zip(
                    columns,
                    ori_data + [model.labels_.tolist()] + pred_xs + [pred_y.tolist()],
                )
            )
        elif model_config.model == "svm":
            ori_data = select_from(
                db,
                model_config.columns,
                model_config.table,
                model_config.dropna,
                model_config.limit,
            )
            ori_data = decimal2float(ori_data)  # 必须全是数字
            length = int(model_config.limit ** (1 / len(ori_data[:-1])))
            model = SVR()
            model.fit(np.array(ori_data[:-1]).T, np.array(ori_data[-1]).T)
            pred_xs = np.meshgrid(
                *[
                    np.linspace(min(ori_d), max(ori_d), length)
                    for ori_d in ori_data[:-1]
                ]
            )
            pred_xs = [pred_x.flatten() for pred_x in pred_xs]
            pred_y = model.predict(np.array(pred_xs).T)
            columns = model_config.columns
            columns = columns + ["pred" + col for col in columns]
            pred_xs = [pred_x.tolist() for pred_x in pred_xs]
            data = dict(zip(columns, ori_data + pred_xs + [pred_y.tolist()]))
        else:
            raise Exception("模型不存在")
        return ModelResponse(success=True, data=data)
    except Exception as e:
        return ModelResponse(success=False, message=str(e), data=None)


def main():
    if debug:
        con = NewConnect(
            connName="test", database="postgres", user="gauss", password="2023@gauss"
        )
        db = py_opengauss.open(generateConnectUrl(con))
        connects.update({con.connName: [db, con]})


main()
