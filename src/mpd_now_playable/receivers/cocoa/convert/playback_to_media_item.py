from Foundation import NSMutableDictionary
from MediaPlayer import (
	MPMediaItemPropertyArtwork,
	MPMediaItemPropertyTitle,
	MPNowPlayingInfoMediaTypeNone,
	MPNowPlayingInfoPropertyMediaType,
	MPNowPlayingInfoPropertyPlaybackQueueCount,
	MPNowPlayingInfoPropertyPlaybackQueueIndex,
	MPNowPlayingInfoPropertyPlaybackRate,
)

from ....playback import Playback
from .song_to_media_item import song_to_media_item
from .to_nsimage import MPD_LOGO


def playback_to_media_item(playback: Playback) -> NSMutableDictionary:
	nowplaying_info = nothing_to_media_item()
	if song := playback.active_song:
		nowplaying_info = song_to_media_item(song)
	nowplaying_info[MPNowPlayingInfoPropertyPlaybackQueueCount] = playback.queue.length
	nowplaying_info[MPNowPlayingInfoPropertyPlaybackQueueIndex] = playback.queue.current
	return nowplaying_info


def nothing_to_media_item() -> NSMutableDictionary:
	nowplaying_info = NSMutableDictionary.dictionary()
	nowplaying_info[MPNowPlayingInfoPropertyMediaType] = MPNowPlayingInfoMediaTypeNone
	nowplaying_info[MPMediaItemPropertyArtwork] = MPD_LOGO
	nowplaying_info[MPMediaItemPropertyTitle] = "MPD (stopped)"
	nowplaying_info[MPNowPlayingInfoPropertyPlaybackRate] = 0.0

	return nowplaying_info
