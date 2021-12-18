import asyncio
from typing import Any, Coroutine


def run_coro(coro: Coroutine) -> Any:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro())
