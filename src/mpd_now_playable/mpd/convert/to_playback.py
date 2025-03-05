from ...config.model import MpdConfig
from ...playback import Playback
from ...playback.queue import Queue
from ...playback.settings import MixRamp, Settings, to_oneshot
from ...tools.types import option_fmap
from ..types import MpdState
from .to_song import to_song


def to_queue(mpd: MpdState) -> Queue:
	return Queue(
		current=option_fmap(int, mpd.current.get("pos")),
		next=int(mpd.status.get("nextsong", 0)),
		length=int(mpd.status["playlistlength"]),
	)


def to_mixramp(mpd: MpdState) -> MixRamp:
	delay = mpd.status.get("mixrampdelay", 0)
	if delay == "nan":
		delay = 0
	return MixRamp(
		db=float(mpd.status.get("mixrampdb", 0)),
		delay=float(delay),
	)


def to_settings(mpd: MpdState) -> Settings:
	return Settings(
		volume=option_fmap(int, mpd.status.get("volume")),
		repeat=mpd.status["repeat"] == "1",
		random=mpd.status["random"] == "1",
		single=to_oneshot(mpd.status["single"]),
		consume=to_oneshot(mpd.status["consume"]),
		crossfade=int(mpd.status.get("xfade", 0)),
		mixramp=to_mixramp(mpd),
	)


def to_playback(config: MpdConfig, mpd: MpdState) -> Playback:
	partition = mpd.status["partition"]
	queue = to_queue(mpd)
	settings = to_settings(mpd)
	return Playback(
		partition=partition,
		queue=queue,
		settings=settings,
		song=to_song(config, mpd),
	)
