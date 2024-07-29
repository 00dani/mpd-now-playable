from dataclasses import dataclass
from typing import Annotated, Literal

from annotated_types import Ge

OneShotFlag = bool | Literal["oneshot"]


def to_oneshot(value: str) -> OneShotFlag:
	match value:
		case "1":
			return True
		case "0":
			return False
		case "oneshot":
			return "oneshot"
	return False


@dataclass(slots=True, kw_only=True)
class MixRamp:
	#: The volume threshold at which MPD will overlap MixRamp-analysed songs,
	#: measured in decibels. Can be set to any float, but sensible values are
	#: typically negative.
	db: float

	#: A delay time in seconds which will be subtracted from the MixRamp
	#: overlap. Must be set to a positive value for MixRamp to work at all -
	#: will be zero if it's disabled.
	delay: float


@dataclass(slots=True, kw_only=True)
class Settings:
	#: The playback volume ranging from 0 to 100 - it will only be available if
	#: MPD has a volume mixer configured.
	volume: int | None

	#: Repeat playback of the queued songs. This setting normally means the
	#: entire queue will be played on repeat, but its behaviour can be
	#: influenced by the other playback mode flags.
	repeat: bool

	#: Play the queued songs in random order. This is distinct from shuffling
	#: the queue, which randomises the queue's order once when you send the
	#: shuffle command and will then play the queue in that new order
	#: repeatedly if asked. If MPD is asked to both repeat and randomise, the
	#: queue is effectively shuffled each time it loops.
	random: bool

	#: Play only a single song. If MPD is asked to repeat, then the current
	#: song will be played repeatedly. Otherwise, when the current song ends
	#: MPD will simply stop playback. Like the consume flag, the single flag
	#: can also be set to "oneshot", which will cause the single flag to be
	#: switched off after it takes effect once (either the current song will
	#: repeat just once, or playback will stop but the single flag will be
	#: switched off).
	single: OneShotFlag

	#: Remove songs from the queue as they're played. This flag can also be set
	#: to "oneshot", which means the currently playing song will be consumed,
	#: and then the flag will automatically be switched off.
	consume: OneShotFlag

	#: The number of seconds to overlap songs when cross-fading between the
	#: current song and the next. Will be zero when the cross-fading feature is
	#: disabled entirely. Curiously, fractional seconds are not supported here,
	#: unlike many other places MPD uses seconds.
	crossfade: Annotated[int, Ge(0)]

	#: Settings for MixRamp-powered cross-fading, which analyses your songs'
	#: volume levels to choose optimal places for cross-fading. This requires
	#: either that the songs have previously been analysed and tagged with
	#: MixRamp information, or that MPD's on the fly mixramp_analyzer has been
	#: enabled.
	mixramp: MixRamp
