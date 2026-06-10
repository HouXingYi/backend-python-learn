import { useCallback, useState } from "react";
import { Link, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { Button, Card, Layout, Menu, Space, Typography, message } from "antd";

import { API_BASE_URL } from "./api/config";
import "./App.css";
import AgentChatPage from "./pages/AgentChatPage";
import CrudPage from "./pages/CrudPage";

type ApiResponse = {
  message: string;
};

function App() {
  const location = useLocation();

  return (
    <Layout className="app-shell">
      <Layout.Header className="app-header">
        <Typography.Title level={4} className="app-title">
          Backend Python Learn
        </Typography.Title>
        <Menu
          className="app-menu"
          theme="dark"
          mode="horizontal"
          selectedKeys={[location.pathname]}
          items={[
            { key: "/", label: <Link to="/">首页</Link> },
            { key: "/crud", label: <Link to="/crud">CRUD</Link> },
            {
              key: "/agent-chat",
              label: <Link to="/agent-chat">Agent Chat</Link>,
            },
          ]}
        />
      </Layout.Header>
      <Layout.Content className="app-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/crud" element={<CrudPage />} />
          <Route path="/agent-chat" element={<AgentChatPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout.Content>
    </Layout>
  );
}

function HomePage() {
  const [loading, setLoading] = useState(false);
  const [apiMessage, setApiMessage] = useState<string>();
  const [messageApi, contextHolder] = message.useMessage();

  const handleRequest = useCallback(async () => {
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/`);

      if (!response.ok) {
        throw new Error(`请求失败：${response.status}`);
      }

      const data = (await response.json()) as ApiResponse;
      setApiMessage(data.message);
      messageApi.success(`后端返回：${data.message}`);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "请求 FastAPI 失败";
      messageApi.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [messageApi]);

  return (
    <section className="page">
      {contextHolder}
      <Card className="demo-card">
        <Space direction="vertical" size="large">
          <Space direction="vertical" size="small">
            <Typography.Title level={2}>FastAPI 调用示例</Typography.Title>
            <Typography.Text type="secondary">
              点击按钮请求 FastAPI 根接口，也可以进入 CRUD 或 Agent Chat 页面继续学习。
            </Typography.Text>
          </Space>

          <Button type="primary" loading={loading} onClick={handleRequest}>
            请求 FastAPI
          </Button>

          {apiMessage ? (
            <Typography.Text>
              当前返回内容：<Typography.Text code>{apiMessage}</Typography.Text>
            </Typography.Text>
          ) : null}
        </Space>
      </Card>
    </section>
  );
}

export default App;
