import { useCallback, useState } from "react";
import { Button, Card, Space, Typography, message } from "antd";

import "./App.css";

type ApiResponse = {
  message: string;
};

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

function App() {
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
    <main className="page">
      {contextHolder}
      <Card className="demo-card">
        <Space direction="vertical" size="large">
          <Space direction="vertical" size="small">
            <Typography.Title level={2}>FastAPI 调用示例</Typography.Title>
            <Typography.Text type="secondary">
              点击按钮请求 FastAPI 根接口，并用 Ant Design message 展示返回结果。
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
    </main>
  );
}

export default App;
