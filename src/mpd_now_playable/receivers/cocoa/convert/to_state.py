from MediaPlayer import (
	MPMusicPlaybackState,
	MPMusicPlaybackStatePaused,
	MPMusicPlaybackStatePlaying,
	MPMusicPlaybackStateStopped,
)

from ....playback.state import PlaybackState

__all__ = ("playback_state_to_cocoa",)


def playback_state_to_cocoa(state: PlaybackState) -> MPMusicPlaybackState:
	mapping: dict[PlaybackState, MPMusicPlaybackState] = {
		PlaybackState.play: MPMusicPlaybackStatePlaying,
		PlaybackState.pause: MPMusicPlaybackStatePaused,
		PlaybackState.stop: MPMusicPlaybackStateStopped,
	}
	return mapping[state]
