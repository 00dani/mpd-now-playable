from typing import Generic, TypeVar

T = TypeVar("T")

class BaseCache(Generic[T]):
	@staticmethod
	def parse_uri_path(path: str) -> dict[str, str]: ...
