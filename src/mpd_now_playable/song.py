from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Literal, Protocol
from uuid import UUID

from pydantic.type_adapter import TypeAdapter


class PlaybackState(StrEnum):
	play = "play"
	pause = "pause"
	stop = "stop"


@dataclass(slots=True)
class HasArtwork:
	data: bytes = field(repr=False)


@dataclass(slots=True)
class NoArtwork:
	def __bool__(self) -> Literal[False]:
		return False


Artwork = HasArtwork | NoArtwork
ArtworkSchema: TypeAdapter[Artwork] = TypeAdapter(HasArtwork | NoArtwork)


def to_artwork(art: bytes | None) -> Artwork:
	if art is None:
		return NoArtwork()
	return HasArtwork(art)


@dataclass(slots=True)
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
	art: Artwork


class SongListener(Protocol):
	def update(self, song: Song | None) -> None: ...
