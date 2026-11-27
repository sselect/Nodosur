"""Bus de eventos en memoria para el dashboard en vivo (Server-Sent Events)."""

import asyncio
import json
from datetime import UTC, datetime


class EventBus:
    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue] = set()

    def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=200)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        self._subscribers.discard(queue)

    @property
    def subscriber_count(self) -> int:
        return len(self._subscribers)

    def publish(self, event: str, data: dict | None = None) -> None:
        payload = {"event": event, "at": datetime.now(UTC).isoformat(), "data": data or {}}
        for queue in list(self._subscribers):
            try:
                queue.put_nowait(payload)
            except asyncio.QueueFull:
                pass  # cliente lento: se pierde el evento, no bloquea al agente


def format_sse(payload: dict) -> str:
    return f"event: {payload['event']}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


bus = EventBus()
