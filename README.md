# backend-learn

这是一个用于学习 Python 后端和前端联调的项目骨架，包含：

- FastAPI 健康检查接口
- FastAPI + SQLAlchemy + MySQL 的 Product CRUD 示例
- deepagents 风格的流式聊天接口，默认 mock，支持切换到 Kimi/Moonshot
- React + Vite + Ant Design 前端页面

## 项目结构

```text
.
├── pyproject.toml
├── README.md
├── docker-compose.yml
├── frontend/
│   └── src/
│       ├── api/
│       ├── pages/
│       ├── App.tsx
│       └── main.tsx
├── src/
│   └── app/
│       ├── agents/
│       ├── core/
│       ├── crud/
│       ├── db/
│       ├── models/
│       ├── routers/
│       ├── schemas/
│       ├── __init__.py
│       └── main.py
└── tests/
    └── test_main.py
```

## 本地运行

复制后端环境变量示例：

```bash
cp .env.example .env
```

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

如果你本地还没有 MySQL，推荐先安装 Docker Desktop，然后启动项目自带的 MySQL：

```bash
docker compose up -d mysql
```

默认连接串在 `.env.example` 中：

```text
DATABASE_URL=mysql+pymysql://app_user:app_password@127.0.0.1:3306/backend_learn
```

首次启动前先安装前端依赖：

```bash
cd frontend
npm install
cd ..
```

推荐使用一键开发命令同时启动后端和前端：

```bash
app-dev
```

`app-dev` 会启动：

- 后端：`http://127.0.0.1:8000`，使用 `uvicorn --reload` 支持热更新
- 前端：`http://127.0.0.1:5173`

按 `Ctrl+C` 会同时停止前端和后端。

如果项目根目录没有 `.env`，`app-dev` 会默认使用本地 SQLite 文件 `dev.db`，方便不安装 MySQL/Docker 时也能运行 CRUD 示例。

也可以只启动 FastAPI 服务：

```bash
app
```

服务启动后，可以访问：

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/docs
```

只启动前端：

```bash
cd frontend
npm install
npm run dev
```

前端页面：

```text
http://127.0.0.1:5173/
http://127.0.0.1:5173/crud
http://127.0.0.1:5173/agent-chat
```

## Kimi 配置

默认 `.env` 中 `AGENT_MODE=mock`，聊天接口不会请求真实 LLM。

拿到 Kimi/Moonshot Key 后，可以改成：

```text
AGENT_MODE=kimi
MOONSHOT_API_KEY=你的 key
KIMI_BASE_URL=https://api.moonshot.ai/v1
KIMI_MODEL=kimi-k2.6
KIMI_THINKING=disabled
```

运行测试：

```bash
pytest
```
