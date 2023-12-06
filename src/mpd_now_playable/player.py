from typing import Protocol

from .song import PlaybackState


class Player(Protocol):
	async def on_play_pause(self) -> PlaybackState:
		...

	async def on_play(self) -> PlaybackState:
		...

	async def on_pause(self) -> PlaybackState:
		...

	async def on_stop(self) -> PlaybackState:
		...

	async def on_next(self) -> None:
		...

	async def on_prev(self) -> None:
		...

	async def on_seek(self, position: float) -> None:
		...
