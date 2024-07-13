from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from ..tools.schema.define import schema
from .artwork import Artwork
from .musicbrainz import MusicBrainzIds


class PlaybackState(StrEnum):
	play = "play"
	pause = "pause"
	stop = "stop"


@schema("https://cdn.00dani.me/m/schemata/mpd-now-playable/song-v1.json")
@dataclass(slots=True)
class Song:
	#: Whether MPD is currently playing, paused, or stopped. Pretty simple.
	state: PlaybackState

	#: The zero-based index of the current song in MPD's queue.
	queue_index: int
	#: The total length of MPD's queue - the last song in the queue will have
	#: the index one less than this, since queue indices are zero-based.
	queue_length: int

	#: The relative path to the current song inside the music directory. MPD
	#: itself uses this path as a stable identifier for the audio file in many
	#: places, so you can safely do the same.
	file: Path

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
	#: Fractional seconds are allowed.
	duration: float

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
