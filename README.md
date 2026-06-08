# backend-learn

这是一个用于学习 Python 的最小标准项目骨架。

## 项目结构

```text
.
├── pyproject.toml
├── README.md
├── src/
│   └── app/
│       ├── __init__.py
│       └── main.py
└── tests/
    └── test_main.py
```

## 本地运行

创建虚拟环境：

```bash
python -m venv .venv
```

激活虚拟环境：

```bash
source .venv/Scripts/activate
```

安装当前项目和开发依赖：

```bash
pip install -e ".[dev]"
```

启动 FastAPI 服务：

```bash
app
```

服务启动后，可以访问：

```text
http://127.0.0.1:8000/
```

交互式接口文档：

```text
http://127.0.0.1:8000/docs
```

运行测试：

```bash
pytest
```
