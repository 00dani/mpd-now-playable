from __future__ import annotations

from contextlib import suppress
from typing import Any, Generic, Optional, TypeVar

from aiocache import Cache
from aiocache.serializers import BaseSerializer
from pydantic.type_adapter import TypeAdapter
from yarl import URL

T = TypeVar("T")

with suppress(ImportError):
	import ormsgpack


class OrmsgpackSerializer(BaseSerializer, Generic[T]):
	DEFAULT_ENCODING = None

	def __init__(self, schema: TypeAdapter[T]):
		super().__init__()
		self.schema = schema

	def dumps(self, value: T) -> bytes:
		return ormsgpack.packb(self.schema.dump_python(value))

	def loads(self, value: Optional[bytes]) -> T | None:
		if value is None:
			return None
		data = ormsgpack.unpackb(value)
		return self.schema.validate_python(data)


def make_cache(schema: TypeAdapter[T], url: URL, namespace: str = "") -> Cache[T]:
	backend = Cache.get_scheme_class(url.scheme)
	if backend == Cache.MEMORY:
		return Cache(backend)

	kwargs: dict[str, Any] = dict(url.query)

	if url.path:
		kwargs.update(backend.parse_uri_path(url.path))

	if url.host:
		kwargs["endpoint"] = url.host

	if url.port:
		kwargs["port"] = url.port

	if url.password:
		kwargs["password"] = url.password

	namespace = ":".join(s for s in [kwargs.pop("namespace", ""), namespace] if s)

	serializer = OrmsgpackSerializer(schema)

	return Cache(backend, serializer=serializer, namespace=namespace, **kwargs)
