from dataclasses import dataclass, field
from typing import Optional

from apischema import alias
from yarl import URL

from .fields import Host, Port, optional

__all__ = ("MpdConfig", "Config")


@dataclass(frozen=True)
class MpdConfig:
	password: Optional[str] = optional()
	host: Host = Host("127.0.0.1")
	port: Port = Port(6600)


@dataclass(frozen=True)
class Config:
	schema: URL = field(
		default=URL("https://cdn.00dani.me/m/schemata/mpd-now-playable/config-v1.json"),
		metadata=alias("$schema"),
	)
	cache: Optional[URL] = optional()
	mpd: MpdConfig = field(default_factory=MpdConfig)
