from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from ..playback.state import PlaybackState
from ..tools.schema.define import schema
from ..tools.schema.fields import Url
from .artwork import Artwork
from .musicbrainz import MusicBrainzIds


@schema("https://cdn.00dani.me/m/schemata/mpd-now-playable/song-v1.json")
@dataclass(slots=True, kw_only=True)
class Song:
	#: Whether MPD is currently playing or paused. Pretty simple.
	state: Literal[PlaybackState.play, PlaybackState.pause]

	#: The relative path to the current song inside the music directory. MPD
	#: itself uses this path as a stable identifier for the audio file in many
	#: places, so you can safely do the same.
	file: Path

	#: An absolute URL referring to the current song, if available. If the
	#: song's a local file and its absolute path can be determined
	#: (mpd-now-playable has been configured with your music directory), then
	#: this field will contain a file:// URL. If the song's remote, then MPD
	#: itself returns an absolute URL in the first place.
	url: Url | None = None

	#: The song's title, if it's been tagged with one. Currently only one title
	#: is supported, since it doesn't make a lot of sense to tag a single audio
	#: file with multiple titles.
	title: str | None

	#: The song's artists. Will be an empty list if the song has not been
	#: tagged with an artist, and may contain multiple values if the song has
	#: been tagged with several artists.
	artist: list[str]
	#: The song's composers. Again, this is permitted to be multivalued.
	composer: list[str]
	#: The name of the song's containing album, which may be multivalued.
	album: list[str]
	#: The album's artists. This is often used to group together songs from a
	#: single album that featured different artists.
	album_artist: list[str]

	#: The track number the song has on its album. This is usually one-based,
	#: but it's just an arbitrary audio tag so a particular album might start
	#: at zero or do something weird with it.
	track: int | None

	#: The disc number of the song on its album. As with the track number, this
	#: is usually one-based, but it doesn't have to be.
	disc: int | None

	#: The song's genre or genres. These are completely arbitrary descriptions
	#: and don't follow any particular standard.
	genre: list[str]

	#: The song's duration as read from its tags, measured in seconds.
	#: Fractional seconds are allowed. The duration may be unavailable for some
	#: sources, such as internet radio streams.
	duration: float | None

	#: How far into the song MPD is, measured in seconds. Fractional seconds
	#: are allowed. This is usually going to be less than or equal to the
	#: song's duration, but because the duration is tagged as metadata and this
	#: value represents the actual elapsed time, it might go higher if the
	#: song's duration tag is inaccurate.
	elapsed: float

	#: The song's cover art, if it has any - the art will be available as bytes
	#: if present, ready to be displayed directly by receivers.
	art: Artwork

	#: The MusicBrainz IDs associated with the song and with its artist and
	#: album, which if present are an extremely accurate way to identify a
	#: given song. They're not always present, though.
	musicbrainz: MusicBrainzIds
