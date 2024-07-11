from dataclasses import dataclass, field
from typing import Literal

from pydantic.type_adapter import TypeAdapter


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
