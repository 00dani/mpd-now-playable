from typing import ClassVar, Optional

from .base import BaseCache
from .serializers import BaseSerializer

class Cache[T](BaseCache[T]):
	MEMORY: ClassVar[type[BaseCache]]
	REDIS: ClassVar[type[BaseCache] | None]
	MEMCACHED: ClassVar[type[BaseCache] | None]

	def __new__(
		cls,
		cache_class: type[BaseCache] = MEMORY,
		*,
		serializer: Optional[BaseSerializer] = None,
		namespace: str = "",
		**kwargs,
	) -> Cache[T]: ...
	@staticmethod
	def get_scheme_class(scheme: str) -> type[BaseCache]: ...
	async def add(self, key: str, value: T, ttl: Optional[int]) -> None: ...
	async def set(self, key: str, value: T, ttl: Optional[int]) -> None: ...  # noqa: A003
	async def get(self, key: str, default: T | None = None) -> T | None: ...
