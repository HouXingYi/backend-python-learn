# frontend

React + Ant Design 前端示例，用于调用当前项目中的 FastAPI 服务。

## 本地开发

安装依赖：

```bash
npm install
```

启动前端：

```bash
npm run dev
```

默认请求后端地址：

```text
http://127.0.0.1:8000
```

如需修改后端地址，可复制 `.env.example` 为 `.env`，并调整：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```
