from functools import wraps
from typing import Any, Callable


class FunctionWithAuthorization:
    def __init__(self, func: Callable[..., Any]) -> None:
        self.func = func
        self.allow_unauthorized = True

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return await self.func(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.func, name)


def allow_unauthorized(func: Callable[..., Any]) -> Callable[..., Any]:
    wrapped_func = FunctionWithAuthorization(func)
    return wraps(func)(wrapped_func)
