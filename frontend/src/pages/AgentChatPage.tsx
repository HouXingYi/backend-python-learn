import { useMemo, useState } from "react";
import { Button, Card, Input, List, Space, Typography, message } from "antd";

import {
  streamAgentChat,
  type ChatMessage,
  type ChatRole,
} from "../api/agent";

type UiMessage = ChatMessage & {
  id: string;
};

function AgentChatPage() {
  const [messageApi, contextHolder] = message.useMessage();
  const [messages, setMessages] = useState<UiMessage[]>([
    {
      id: crypto.randomUUID(),
      role: "assistant",
      content:
        "你好，我是一个通用 AI 助手示例。你可以随便说点什么，我会尽量帮你梳理想法或给出下一步建议。",
    },
  ]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);

  const requestMessages = useMemo<ChatMessage[]>(
    () =>
      messages
        .filter(({ content }) => content.trim().length > 0)
        .map(({ role, content }) => ({
          role,
          content,
        })),
    [messages],
  );

  const sendMessage = async () => {
    const content = input.trim();
    if (!content || streaming) {
      return;
    }

    const userMessage: UiMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content,
    };
    const assistantId = crypto.randomUUID();
    const assistantMessage: UiMessage = {
      id: assistantId,
      role: "assistant",
      content: "",
    };
    const nextMessages = [...requestMessages, userMessage];

    setInput("");
    setStreaming(true);
    setMessages((current) => [...current, userMessage, assistantMessage]);

    try {
      await streamAgentChat(nextMessages, {
        onToken: (token) => {
          setMessages((current) =>
            current.map((item) =>
              item.id === assistantId
                ? { ...item, content: item.content + token }
                : item,
            ),
          );
        },
        onError: (errorMessage) => {
          messageApi.error(errorMessage);
        },
      });
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : "Agent 请求失败");
    } finally {
      setStreaming(false);
    }
  };

  const clearMessages = () => {
    setMessages([]);
  };

  return (
    <section className="content-page">
      {contextHolder}
      <Card>
        <Space direction="vertical" size="large" className="full-width">
          <Space direction="vertical" size="small">
            <Typography.Title level={2}>Deepagents 流式聊天</Typography.Title>
            <Typography.Text type="secondary">
              后端通过 SSE 返回 token 流。默认 mock，可在 `.env` 中填入 LiteLLM 网关配置后切换真实调用。
            </Typography.Text>
          </Space>

          <List
            className="chat-list"
            dataSource={messages}
            locale={{ emptyText: "还没有消息，发送一句话开始测试。" }}
            renderItem={(item) => (
              <List.Item className={`chat-item chat-item-${item.role}`}>
                <Card size="small" className="chat-bubble">
                  <Typography.Text strong>{roleLabel(item.role)}</Typography.Text>
                  <Typography.Paragraph className="chat-content">
                    {item.content || (streaming ? "正在生成..." : "")}
                  </Typography.Paragraph>
                </Card>
              </List.Item>
            )}
          />

          <Space.Compact className="full-width">
            <Input.TextArea
              autoSize={{ minRows: 2, maxRows: 5 }}
              value={input}
              placeholder="输入你想问 agent 的内容"
              onChange={(event) => setInput(event.target.value)}
              onPressEnter={(event) => {
                if (!event.shiftKey) {
                  event.preventDefault();
                  void sendMessage();
                }
              }}
            />
            <Button type="primary" loading={streaming} onClick={sendMessage}>
              发送
            </Button>
          </Space.Compact>

          <Button onClick={clearMessages}>清空会话</Button>
        </Space>
      </Card>
    </section>
  );
}

function roleLabel(role: ChatRole): string {
  if (role === "user") {
    return "你";
  }
  if (role === "system") {
    return "系统";
  }
  return "Agent";
}

export default AgentChatPage;
