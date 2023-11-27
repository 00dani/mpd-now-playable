from typing import Generic, Optional, TypeVar

T = TypeVar('T')

class Cache(Generic[T]):
    async def add(self, key: str, value: T, ttl: Optional[int]) -> None: ...
    async def set(self, key: str, value: T, ttl: Optional[int]) -> None: ... # noqa: A003
    async def get(self, key: str, default: T | None = None) -> T | None: ...
