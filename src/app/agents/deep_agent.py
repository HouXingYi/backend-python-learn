import asyncio
from collections.abc import AsyncGenerator

from app.core.config import Settings
from app.schemas.agent import ChatMessage


MOCK_RESPONSE = (
    "这是一个 mock 的 deepagents 流式回复。"
    "等你把 MOONSHOT_API_KEY 填进 .env，并把 AGENT_MODE 设置为 kimi 后，"
    "后端会尝试通过 Kimi 的 OpenAI 兼容接口调用真实模型。"
)


async def stream_agent_reply(
    messages: list[ChatMessage],
    settings: Settings,
) -> AsyncGenerator[str, None]:
    if settings.use_mock_agent:
        async for token in _stream_mock_reply(messages):
            yield token
        return

    async for token in _stream_kimi_reply(messages, settings):
        yield token


async def _stream_mock_reply(
    messages: list[ChatMessage],
) -> AsyncGenerator[str, None]:
    last_user_message = next(
        (message.content for message in reversed(messages) if message.role == "user"),
        "",
    )
    reply = f"{MOCK_RESPONSE}\n\n你刚才说：{last_user_message}"

    for char in reply:
        await asyncio.sleep(0.02)
        yield char


async def _stream_kimi_reply(
    messages: list[ChatMessage],
    settings: Settings,
) -> AsyncGenerator[str, None]:
    try:
        from deepagents import create_deep_agent
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise RuntimeError(
            "缺少 deepagents 或 langchain-openai 依赖，请先安装后端依赖。",
        ) from exc

    model = ChatOpenAI(
        api_key=settings.moonshot_api_key,
        base_url=settings.kimi_base_url,
        model=settings.kimi_model,
        streaming=True,
        timeout=settings.kimi_timeout_seconds,
        max_retries=0,
        stream_chunk_timeout=settings.kimi_timeout_seconds,
        extra_body={
            "thinking": {"type": settings.kimi_thinking},
        },
    )
    agent = create_deep_agent(
        model=model,
        tools=[],
        system_prompt="你是一个用于学习后端开发的中文助教，回答要清晰、简洁、可操作。",
    )

    payload = {
        "messages": [
            {"role": message.role, "content": message.content}
            for message in messages
        ],
    }

    stream = agent.stream(
        payload,
        stream_mode="messages",
        version="v2",
    )

    try:
        while True:
            has_chunk, chunk = await asyncio.to_thread(_next_stream_chunk, stream)
            if not has_chunk:
                break

            token = _extract_token(chunk)
            if token:
                yield token
    except Exception as exc:
        raise RuntimeError(_format_kimi_error(exc, settings)) from exc


def _extract_token(chunk: object) -> str:
    if not isinstance(chunk, dict):
        return ""

    data = chunk.get("data")
    if isinstance(data, dict):
        chunk_data = data.get("chunk")
        if hasattr(chunk_data, "content") and isinstance(chunk_data.content, str):
            return chunk_data.content

        content = data.get("content")
        if isinstance(content, str):
            return content

    return ""


def _next_stream_chunk(stream: object) -> tuple[bool, object | None]:
    try:
        return True, next(stream)  # type: ignore[arg-type]
    except StopIteration:
        return False, None


def _format_kimi_error(exc: Exception, settings: Settings) -> str:
    message = str(exc)
    lower_message = message.lower()

    if "invalid authentication" in lower_message or "401" in lower_message:
        return (
            "Kimi API 认证失败：请检查 MOONSHOT_API_KEY 是否有效，"
            f"并确认它和 KIMI_BASE_URL={settings.kimi_base_url} 属于同一个平台。"
        )

    if "timed out" in lower_message or "timeout" in lower_message:
        return (
            f"Kimi API 请求超时：当前地址 {settings.kimi_base_url} 在 "
            f"{settings.kimi_timeout_seconds:g} 秒内没有响应。"
            "请检查网络、代理、防火墙，或确认 KIMI_BASE_URL 是否与官网控制台一致。"
        )

    return f"Kimi API 请求失败：{message}"
