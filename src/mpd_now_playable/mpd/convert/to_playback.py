from ...config.model import MpdConfig
from ...playback import Playback
from ...playback.queue import Queue
from ...playback.settings import Settings, to_oneshot
from ...tools.types import option_fmap
from ..types import MpdState
from .to_song import to_song


def to_queue(mpd: MpdState) -> Queue:
	return Queue(
		current=int(mpd.current["pos"]),
		next=int(mpd.status["nextsong"]),
		length=int(mpd.status["playlistlength"]),
	)


def to_settings(mpd: MpdState) -> Settings:
	return Settings(
		volume=option_fmap(int, mpd.status.get("volume")),
		repeat=mpd.status["repeat"] == "1",
		random=mpd.status["random"] == "1",
		single=to_oneshot(mpd.status["single"]),
		consume=to_oneshot(mpd.status["consume"]),
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
