from enum import StrEnum
from typing import Protocol

from attrs import define, field


class PlaybackState(StrEnum):
	play = "play"
	pause = "pause"
	stop = "stop"


@define
class Song:
	state: PlaybackState
	title: str
	artist: str
	album: str
	album_artist: str
	duration: float
	elapsed: float
	art: bytes | None = field(repr=lambda a: "<has art>" if a else "<no art>")


class SongListener(Protocol):
	def update(self, song: Song | None) -> None:
		...
