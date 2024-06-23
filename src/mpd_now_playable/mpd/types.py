from typing import Literal, NotRequired, Protocol, TypedDict

from ..tools.types import MaybePlural


class MpdStateHandler(Protocol):
	async def get_art(self, file: str) -> bytes | None: ...

	async def refresh(self) -> None: ...


BooleanFlag = Literal["0", "1"]

OneshotFlag = Literal[BooleanFlag, "oneshot"]


# This is not the complete status response from MPD, just the parts of it mpd-now-playable uses.
class StatusResponse(TypedDict):
	state: Literal["play", "stop", "pause"]

	# The total duration and elapsed playback of the current song, measured in seconds. Fractional seconds are allowed.
	duration: str
	elapsed: str

	# The volume value ranges from 0-100. It may be omitted from
	# the response entirely if MPD has no volume mixer configured.
	volume: NotRequired[str]

	# Various toggle-able music playback settings, which can be addressed and modified by Now Playing.
	repeat: BooleanFlag
	random: BooleanFlag
	single: OneshotFlag
	consume: OneshotFlag

	# Partitions essentially let one MPD server act as multiple music players.
	# For most folks, this will just be "default", but mpd-now-playable will
	# eventually support addressing specific partitions. Eventually.
	partition: str

	# The total number of items in the play queue, which is called the "playlist" throughout the MPD protocol for legacy reasons.
	playlistlength: str

	# The format of decoded audio MPD is producing, expressed as a string in the form "samplerate:bits:channels".
	audio: str


# All of these are metadata tags read from your music, and are strictly
# optional. mpd-now-playable will work better if your music is properly
# tagged, since then it can pass more information on to Now Playing, but it
# should work fine with completely untagged music too.
class CurrentSongTags(TypedDict, total=False):
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
	musicbrainz_albumid: str
	musicbrainz_albumartistid: str
	musicbrainz_releasetrackid: str
	musicbrainz_artistid: str
	musicbrainz_trackid: str


class CurrentSongResponse(CurrentSongTags):
	# The name of the music file currently being played, as MPD understands
	# it. For locally stored music files, this'll just be a simple file path
	# relative to your music directory.
	file: str
	# The index of the song in the play queue. Will change if you shuffle or
	# otherwise reorder the playlist.
	pos: str


ReadPictureResponse = TypedDict("ReadPictureResponse", {"binary": bytes})
