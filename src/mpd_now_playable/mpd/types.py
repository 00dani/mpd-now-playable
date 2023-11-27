from typing import Protocol, TypedDict


class MpdStateHandler(Protocol):
	async def readpicture(self, file: str) -> bytes | None:
		...

	async def refresh(self) -> None:
		...


class StatusResponse(TypedDict):
	volume: str
	repeat: str
	random: str
	single: str
	consume: str
	partition: str
	playlist: str
	playlistlength: str
	mixrampdb: str
	state: str
	song: str
	songid: str
	time: str
	elapsed: str
	bitrate: str
	duration: str
	audio: str
	nextsong: str
	nextsongid: str


CurrentSongResponse = TypedDict(
	"CurrentSongResponse",
	{
		"file": str,
		"last-modified": str,
		"format": str,
		"artist": str,
		"albumartist": str,
		"artistsort": str,
		"albumartistsort": str,
		"title": str,
		"album": str,
		"track": str,
		"date": str,
		"originaldate": str,
		"composer": str,
		"disc": str,
		"label": str,
		"musicbrainz_albumid": str,
		"musicbrainz_albumartistid": str,
		"musicbrainz_releasetrackid": str,
		"musicbrainz_artistid": str,
		"musicbrainz_trackid": str,
		"time": str,
		"duration": str,
		"pos": str,
		"id": str,
	},
)

ReadPictureResponse = TypedDict("ReadPictureResponse", {"binary": bytes})
