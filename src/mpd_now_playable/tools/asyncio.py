import asyncio
from collections.abc import Coroutine
from contextvars import Context
from typing import Optional

__all__ = ("run_background_task",)

background_tasks: set[asyncio.Task[None]] = set()


def run_background_task(
	coro: Coroutine[None, None, None],
	*,
	name: Optional[str] = None,
	context: Optional[Context] = None,
) -> None:
	task = asyncio.create_task(coro, name=name, context=context)
	background_tasks.add(task)
	task.add_done_callback(background_tasks.discard)
