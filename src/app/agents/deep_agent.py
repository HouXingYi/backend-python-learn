import asyncio
from collections.abc import AsyncGenerator

from app.core.config import Settings
from app.schemas.agent import ChatMessage


MOCK_RESPONSE = (
    "这是一个 mock 的 deepagents 流式回复。"
    "等你把 LITELLM_API_KEY 填进 .env，并把 AGENT_MODE 设置为 litellm 后，"
    "应用会尝试通过 LiteLLM 网关的 OpenAI 兼容接口调用真实模型。"
)


async def stream_agent_reply(
    messages: list[ChatMessage],
    settings: Settings,
) -> AsyncGenerator[str, None]:
    if settings.use_mock_agent:
        async for token in _stream_mock_reply(messages):
            yield token
        return

    async for token in _stream_litellm_reply(messages, settings):
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


async def _stream_litellm_reply(
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
        api_key=settings.litellm_api_key,
        base_url=settings.litellm_base_url,
        model=settings.litellm_model_name,
        streaming=True,
        timeout=settings.litellm_timeout_seconds,
        max_retries=0,
        stream_chunk_timeout=settings.litellm_timeout_seconds,
        extra_body=_litellm_extra_body(settings),
    )
    agent = create_deep_agent(
        model=model,
        tools=[],
        system_prompt="你是一个通用的中文 AI 助手。用户可能还没有明确目标，请用自然、友好、清晰的方式回应，必要时可以帮用户梳理想法或给出可操作的下一步。",
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
        raise RuntimeError(_format_litellm_error(exc, settings)) from exc


def _litellm_extra_body(settings: Settings) -> dict[str, object] | None:
    if not settings.litellm_thinking:
        return None

    return {"thinking": {"type": settings.litellm_thinking}}


def _extract_token(chunk: object) -> str:
    if not isinstance(chunk, dict):
        return ""

    data = chunk.get("data")
    if isinstance(data, (tuple, list)) and data:
        chunk_data = data[0]
        if hasattr(chunk_data, "content") and isinstance(chunk_data.content, str):
            return chunk_data.content

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


def _format_litellm_error(exc: Exception, settings: Settings) -> str:
    message = str(exc)
    lower_message = message.lower()

    if "invalid authentication" in lower_message or "401" in lower_message:
        return (
            "LiteLLM 网关认证失败：请检查 LITELLM_API_KEY 是否有效，"
            f"并确认它和 LITELLM_BASE_URL={settings.litellm_base_url} 属于同一个网关。"
        )

    if "timed out" in lower_message or "timeout" in lower_message:
        return (
            f"LiteLLM 网关请求超时：当前地址 {settings.litellm_base_url} 在 "
            f"{settings.litellm_timeout_seconds:g} 秒内没有响应。"
            "请检查网络、代理、防火墙，或确认 LITELLM_BASE_URL 是否与网关地址一致。"
        )

    return f"LiteLLM 网关请求失败：{message}"
