import { API_BASE_URL } from "./config";

export type ChatRole = "user" | "assistant" | "system";

export type ChatMessage = {
  role: ChatRole;
  content: string;
};

type StreamHandlers = {
  onToken: (token: string) => void;
  onDone?: () => void;
  onError?: (message: string) => void;
};

export async function streamAgentChat(
  messages: ChatMessage[],
  handlers: StreamHandlers,
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/agent/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ messages }),
  });

  if (!response.ok || !response.body) {
    throw new Error(`请求失败：${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";

    for (const rawEvent of events) {
      handleEvent(rawEvent, handlers);
    }
  }

  if (buffer) {
    handleEvent(buffer, handlers);
  }
}

function handleEvent(rawEvent: string, handlers: StreamHandlers): void {
  const event = rawEvent
    .split("\n")
    .find((line) => line.startsWith("event: "))
    ?.replace("event: ", "");
  const data = rawEvent
    .split("\n")
    .find((line) => line.startsWith("data: "))
    ?.replace("data: ", "");

  if (!event || !data) {
    return;
  }

  const payload = JSON.parse(data) as { content?: string; message?: string };

  if (event === "message" && payload.content) {
    handlers.onToken(payload.content);
  }

  if (event === "done") {
    handlers.onDone?.();
  }

  if (event === "error") {
    handlers.onError?.(payload.message ?? "Agent 请求失败");
  }
}
