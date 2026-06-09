import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.agents.deep_agent import stream_agent_reply
from app.core.config import Settings, get_settings
from app.schemas.agent import ChatRequest

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/chat/stream")
async def stream_chat(
    chat_request: ChatRequest,
    settings: Settings = Depends(get_settings),
) -> StreamingResponse:
    async def event_stream() -> AsyncGenerator[str, None]:
        try:
            async for token in stream_agent_reply(chat_request.messages, settings):
                yield _sse("message", {"content": token})
            yield _sse("done", {})
        except Exception as exc:
            yield _sse("error", {"message": str(exc)})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def _sse(event: str, data: dict[str, object]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
