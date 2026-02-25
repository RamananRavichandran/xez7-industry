import asyncio
import functools
import random
import time
from typing import Any, Awaitable, Callable, ParamSpec, TypeVar

from .logging import get_logger


P = ParamSpec("P")
R = TypeVar("R")

logger = get_logger(__name__)


def _compute_backoff(base: float, factor: float, attempt: int, jitter: float) -> float:
    delay = base * (factor ** attempt)
    if jitter:
        delay += random.uniform(0, jitter)
    return delay


def retry(
    *,
    attempts: int = 3,
    base_delay: float = 0.5,
    factor: float = 2.0,
    jitter: float = 0.1,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Retry decorator for sync functions with exponential backoff.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exc: BaseException | None = None
            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:  # type: ignore[misc]
                    last_exc = exc
                    delay = _compute_backoff(base_delay, factor, attempt, jitter)
                    logger.warning(
                        "Retrying %s due to %s (attempt %s/%s, delay=%.2fs)",
                        func.__name__,
                        exc,
                        attempt + 1,
                        attempts,
                        delay,
                    )
                    time.sleep(delay)
            if last_exc:
                raise last_exc
            raise RuntimeError("Retry decorator failed without exception.")

        return wrapper

    return decorator


def async_retry(
    *,
    attempts: int = 3,
    base_delay: float = 0.5,
    factor: float = 2.0,
    jitter: float = 0.1,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """
    Retry decorator for async functions with exponential backoff.
    """

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exc: BaseException | None = None
            for attempt in range(attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as exc:  # type: ignore[misc]
                    last_exc = exc
                    delay = _compute_backoff(base_delay, factor, attempt, jitter)
                    logger.warning(
                        "Retrying async %s due to %s (attempt %s/%s, delay=%.2fs)",
                        func.__name__,
                        exc,
                        attempt + 1,
                        attempts,
                        delay,
                    )
                    await asyncio.sleep(delay)
            if last_exc:
                raise last_exc
            raise RuntimeError("Async retry decorator failed without exception.")

        return wrapper

    return decorator

