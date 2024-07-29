from dataclasses import dataclass
from typing import Literal, NotRequired, Protocol, TypedDict

from ..song.musicbrainz import MusicBrainzTags
from ..tools.types import MaybePlural


class MpdStateHandler(Protocol):
	async def get_art(self, file: str) -> bytes | None: ...

	async def refresh(self) -> None: ...


BooleanFlag = Literal["0", "1"]

OneshotFlag = Literal[BooleanFlag, "oneshot"]


# This is not the complete status response from MPD, just the parts of it mpd-now-playable uses.
class StatusResponse(TypedDict):
	state: Literal["play", "stop", "pause"]

	# The total duration and elapsed playback of the current song, measured in
	# seconds. Fractional seconds are allowed. The duration field may be
	# omitted because MPD cannot determine the duration of certain sources,
	# such as Internet radio streams.
	duration: NotRequired[str]
	elapsed: str

	# The volume value ranges from 0-100. It may be omitted from
	# the response entirely if MPD has no volume mixer configured.
	volume: NotRequired[str]

	# Various toggle-able music playback settings, which can be addressed and modified by Now Playing.
	repeat: BooleanFlag
	random: BooleanFlag
	single: OneshotFlag
	consume: OneshotFlag

	# The configured crossfade time in seconds. Omitted if crossfading isn't
	# enabled. Fractional seconds are *not* allowed for this field.
	xfade: NotRequired[str]

	# The volume threshold at which MixRamp-compatible songs will be
	# overlapped, measured in decibels. Will usually be negative, and is
	# permitted to be fractional.
	mixrampdb: NotRequired[str]

	# A number of seconds to subtract from the overlap computed by MixRamp.
	# Must be positive for MixRamp to work and is permitted to be fractional.
	# Can be set to "nan" to disable MixRamp and use basic crossfading instead.
	mixrampdelay: NotRequired[str]

	# Partitions essentially let one MPD server act as multiple music players.
	# For most folks, this will just be "default", but mpd-now-playable will
	# eventually support addressing specific partitions. Eventually.
	partition: str

	# The total number of items in the play queue, which is called the "playlist" throughout the MPD protocol for legacy reasons.
	playlistlength: str

	# The zero-based index of the song that will play when the current song
	# ends, taking into account repeat and random playback settings.
	nextsong: str

	# The format of decoded audio MPD is producing, expressed as a string in the form "samplerate:bits:channels".
	audio: str


# All of these are metadata tags read from your music, and are strictly
# optional. mpd-now-playable will work better if your music is properly
# tagged, since then it can pass more information on to Now Playing, but it
# should work fine with completely untagged music too.
class CurrentSongTags(MusicBrainzTags, total=False):
	artist: MaybePlural[str]
	albumartist: MaybePlural[str]
	artistsort: MaybePlural[str]
	albumartistsort: MaybePlural[str]
	title: str
	album: MaybePlural[str]
	track: str
	date: str
	originaldate: str
	composer: MaybePlural[str]
	disc: str
	label: str
	genre: MaybePlural[str]


class CurrentSongResponse(CurrentSongTags):
	# The name of the music file currently being played, as MPD understands
	# it. For locally stored music files, this'll just be a simple file path
	# relative to your music directory.
	file: str
	# The index of the song in the play queue. Will change if you shuffle or
	# otherwise reorder the playlist.
	pos: str


ReadPictureResponse = TypedDict("ReadPictureResponse", {"binary": bytes})


@dataclass
class MpdState:
	status: StatusResponse
	current: CurrentSongResponse
	art: bytes | None = None
