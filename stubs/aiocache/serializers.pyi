from abc import ABC, abstractmethod
from typing import Any, Optional

class BaseSerializer(ABC):
	DEFAULT_ENCODING: Optional[str] = "utf-8"
	@abstractmethod
	def dumps(self, value: Any, /) -> Any: ...
	@abstractmethod
	def loads(self, value: Any, /) -> Any: ...

class PickleSerializer(BaseSerializer):
	DEFAULT_ENCODING = None
	def dumps(self, value: Any, /) -> Any: ...
	def loads(self, value: Any, /) -> Any: ...
