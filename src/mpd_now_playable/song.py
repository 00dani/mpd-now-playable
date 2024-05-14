from enum import StrEnum
from pathlib import Path
from typing import Protocol
from uuid import UUID

from attrs import define, field


class PlaybackState(StrEnum):
	play = "play"
	pause = "pause"
	stop = "stop"


@define
class Song:
	state: PlaybackState
	queue_index: int
	queue_length: int
	file: Path
	musicbrainz_trackid: UUID | None
	musicbrainz_releasetrackid: UUID | None
	title: str | None
	artist: str | None
	composer: str | None
	album: str | None
	album_artist: str | None
	track: int | None
	disc: int | None
	genre: str | None
	duration: float
	elapsed: float
	art: bytes | None = field(repr=lambda a: "<has art>" if a else "<no art>")


class SongListener(Protocol):
	def update(self, song: Song | None) -> None:
		...
