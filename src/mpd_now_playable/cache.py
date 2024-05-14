from __future__ import annotations

from contextlib import suppress
from typing import Any, Optional, TypeVar
from urllib.parse import parse_qsl, urlparse

from aiocache import Cache
from aiocache.serializers import BaseSerializer, PickleSerializer

T = TypeVar("T")

HAS_ORMSGPACK = False
with suppress(ImportError):
	import ormsgpack

	HAS_ORMSGPACK = True


class OrmsgpackSerializer(BaseSerializer):
	DEFAULT_ENCODING = None

	def dumps(self, value: Any) -> bytes:
		return ormsgpack.packb(value)

	def loads(self, value: Optional[bytes]) -> Any:
		if value is None:
			return None
		return ormsgpack.unpackb(value)


def make_cache(url: str, namespace: str = "") -> Cache[T]:
	parsed_url = urlparse(url)
	backend = Cache.get_scheme_class(parsed_url.scheme)
	if backend == Cache.MEMORY:
		return Cache(backend)
	kwargs: dict[str, Any] = dict(parse_qsl(parsed_url.query))

	if parsed_url.path:
		kwargs.update(backend.parse_uri_path(parsed_url.path))

	if parsed_url.hostname:
		kwargs["endpoint"] = parsed_url.hostname

	if parsed_url.port:
		kwargs["port"] = parsed_url.port

	if parsed_url.password:
		kwargs["password"] = parsed_url.password

	namespace = ":".join(s for s in [kwargs.pop("namespace", ""), namespace] if s)

	serializer = OrmsgpackSerializer if HAS_ORMSGPACK else PickleSerializer

	return Cache(backend, serializer=serializer(), namespace=namespace, **kwargs)
