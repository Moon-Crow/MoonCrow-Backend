先安装依赖，见 `requirements.txt`

服务器运行指令见 `server.sh`，注意修改 `HOST` 字段。

如果运行出现找不到 .so 文件，试着运行下面的命令

```shell
ln -s /opt/software/openGauss/libcgroup/lib/* /usr/lib/
ln -s /opt/software/openGauss/libcgroup/lib/* /usr/lib64/
```

运行 `test.py` 测试服务器是否正常工作（同样，需要修改 `HOST`），如果正常，四个请求的 success 字段都为 true，且最后 `/model` 会输出一长串数字。