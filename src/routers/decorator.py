from typing import Any, Awaitable, Callable

unauthorized_endpoints: set[str] = set()


def allow_unauthorized(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    unauthorized_endpoints.add(func.__name__)
    return func
