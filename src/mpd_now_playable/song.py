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
	artist: list[str]
	composer: list[str]
	album: list[str]
	album_artist: list[str]
	track: int | None
	disc: int | None
	genre: list[str]
	duration: float
	elapsed: float
	art: bytes | None = field(repr=lambda a: "<has art>" if a else "<no art>")


class SongListener(Protocol):
	def update(self, song: Song | None) -> None: ...
