from typing import Callable, Protocol, Self, TypeVar

from pydantic.type_adapter import TypeAdapter
from yarl import URL

T = TypeVar("T")


class ModelWithSchema(Protocol):
	@property
	def id(self) -> URL: ...
	@property
	def schema(self) -> TypeAdapter[Self]: ...


def schema(schema_id: str) -> Callable[[type[T]], type[T]]:
	def decorate(clazz: type[T]) -> type[T]:
		type.__setattr__(clazz, "id", URL(schema_id))
		type.__setattr__(clazz, "schema", TypeAdapter(clazz))
		return clazz

	return decorate
