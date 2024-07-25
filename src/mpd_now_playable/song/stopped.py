from dataclasses import dataclass, field
from typing import Literal

from ..playback.state import PlaybackState


@dataclass(slots=True, kw_only=True)
class Stopped:
	state: Literal[PlaybackState.stop] = field(default=PlaybackState.stop, repr=False)
