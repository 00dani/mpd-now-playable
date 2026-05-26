from mpd_now_playable.config.model import MpdConfig
from mpd_now_playable.mpd.convert.to_song import to_song
from mpd_now_playable.mpd.types import MpdState


def test_to_song_accepts_single_value_track_and_disc_lists() -> None:
	mpd = MpdState(
		status={"state": "play", "elapsed": "1.25", "duration": "3.5"},
		current={
			"file": "Artist/Album/Track.flac",
			"pos": "0",
			"track": ["7"],
			"disc": ["2"],
		},
	)

	song = to_song(MpdConfig(), mpd)

	assert song.track == 7
	assert song.disc == 2
