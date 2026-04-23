"""Utilitário para executar corrotinas em tasks Celery síncronas.

Mantém um event loop persistente por processo para evitar problemas
com clients async (ex.: Motor) quando asyncio.run fecha o loop.
"""

import asyncio
from threading import Lock
from typing import Awaitable, TypeVar


_T = TypeVar("_T")
_loop: asyncio.AbstractEventLoop | None = None
_loop_lock = Lock()


def run_async(coro: Awaitable[_T]) -> _T:
    """Executa coroutine em loop persistente do processo atual."""
    global _loop

    with _loop_lock:
        if _loop is None or _loop.is_closed():
            _loop = asyncio.new_event_loop()
            asyncio.set_event_loop(_loop)

        return _loop.run_until_complete(coro)
