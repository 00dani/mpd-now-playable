from dataclasses import dataclass, field
from typing import Optional

from ..tools.schema.define import schema
from .fields import Host, Password, Port, Url

__all__ = ("MpdConfig", "Config")


@dataclass(slots=True)
class MpdConfig:
	#: The password required to connect to your MPD instance, if you need one.
	password: Optional[Password] = None
	#: The hostname or IP address of your MPD server. If you're running MPD
	#: on your local machine, you don't need to configure this.
	host: Host = Host("127.0.0.1")
	#: The port on which to connect to MPD. Unless you're managing multiple MPD
	#: servers on one machine for some reason, you probably haven't changed this
	#: from the default port, 6600.
	port: Port = Port(6600)


@schema("https://cdn.00dani.me/m/schemata/mpd-now-playable/config-v1.json")
@dataclass(slots=True)
class Config:
	#: A URL describing a cache service for mpd-now-playable to use. Supported
	#: protocols are memory://, redis://, and memcached://.
	cache: Optional[Url] = None
	mpd: MpdConfig = field(default_factory=MpdConfig)
