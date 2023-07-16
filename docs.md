> 返回一律默认是 json 格式

##### post `/connect`

连接数据库

- connect_name: 用户指定的连接名，用于区分连接，比如 connect1
- user: 如 gauss
- passwd: 如 2023@gauss
- db: 如 postgres
- host: 主机，可空，默认 127.0.0.1
- port: 端口，可空，默认 15400

-------

- success: 指示是否成功


##### post `/demo`

指示后台创建一个 demo 数据库，并向其中生成并插入数据（比如 skelarn 里面的一些示例数据集，或者自己随机的，需要有一些统计价值，方便后面画图）

- connect_name: 之前连接时候的连接名，用于区分（实际上可能没用，当我们只有一个连接在线时）
- table_name: 如 emp
- dataset: 用于指定创建哪个数据库，后端开发时再补充，如 salary，然后后端就创建一个有 100 行的，有姓名和工资两个列的数据库，具体长什么样，后端记得在文档里补充

---------

- success: 指示是否成功

##### get `/model`

建模

- connect_name: 之前连接时候的连接名，用于区分（实际上可能没用，当我们只有一个连接在线时）
- model: 如 linear
- x: json 格式的列表， 比如 `["col1", "col2"]`
- y: json 格式的列表，比如 `["col3"]`

---------

- result: 一个字符串，比如 `col3 = col1 + col2`，视情况设计一个可以显示的文本型结果
- img: 一个网址，python 画出来的图，无论是本地的 `127.0.0.1:port/img/123` （见 https://fastapi.tiangolo.com/zh/tutorial/static-files/ 但我不确定这是否可以）还是用其他服务器托管（图床等），都可以。

##### get `/chat`

chat 也应该基于已经有的连接

- connect_name: 之前连接时候的连接名，用于区分（实际上可能没用，当我们只有一个连接在线时）
- message: 聊天内容，比如 "将emp表生成为一个 csv" 或 "画出 emp 表里 x 和 y 的线性关系"）

--------

- type: "chat" 表示正常的 chat，比如生成一个 csv。"op:" 表示调用上面非 chat 的接口（即用聊天的方法调用了以上接口，比如建模）
- response：回应的文本内容（当 type = "op" 时，返回一个字典，相当于以上接口的返回，但是还得多一个词条指示是哪个接口，比如 "type: /model"）
- url: 比如图片，或者是 csv 文件链接等

