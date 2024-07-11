from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from .artwork import Artwork
from .musicbrainz import MusicBrainzIds


class PlaybackState(StrEnum):
	play = "play"
	pause = "pause"
	stop = "stop"


@dataclass(slots=True)
class Song:
	state: PlaybackState
	queue_index: int
	queue_length: int
	file: Path
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
	musicbrainz: MusicBrainzIds
