from dataclasses import dataclass

from pydantic import Field

from ..song.song import Song
from ..song.stopped import Stopped
from ..tools.schema.define import schema
from .queue import Queue
from .settings import Settings


@schema("https://static.00dani.me/m/schemata/mpd-now-playable/playback-v1.json")
@dataclass(slots=True, kw_only=True)
class Playback:
	#: The MPD partition this playback information came from. Essentially, MPD
	#: can act as multiple music player servers simultaneously, distinguished
	#: by name. For most users, this will always be "default".
	partition: str

	#: Stats about MPD's song queue, including the current song and next song's
	#: indices in it.
	queue: Queue

	#: Playback settings such as volume and repeat mode.
	settings: Settings

	#: Information about the current song itself. MPD provides none of this
	#: information if its playback is currently stopped, so mpd-now-playable
	#: doesn't either and will give you a Stopped instead in that case.
	song: Song | Stopped = Field(discriminator="state")

	@property
	def active_song(self) -> Song | None:
		if isinstance(self.song, Song):
			return self.song
		return None
