from __future__ import annotations

from contextlib import suppress
from typing import Any, Optional, TypeVar

from aiocache import Cache
from aiocache.serializers import BaseSerializer, PickleSerializer
from yarl import URL

T = TypeVar("T")

HAS_ORMSGPACK = False
with suppress(ImportError):
	import ormsgpack

	HAS_ORMSGPACK = True


class OrmsgpackSerializer(BaseSerializer):
	DEFAULT_ENCODING = None

	def dumps(self, value: object) -> bytes:
		return ormsgpack.packb(value)

	def loads(self, value: Optional[bytes]) -> object:
		if value is None:
			return None
		return ormsgpack.unpackb(value)


def make_cache(url: URL, namespace: str = "") -> Cache[T]:
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

	serializer = OrmsgpackSerializer if HAS_ORMSGPACK else PickleSerializer

	return Cache(backend, serializer=serializer(), namespace=namespace, **kwargs)
