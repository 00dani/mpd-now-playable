from collections.abc import AsyncIterator, Sequence
from typing import Literal

from mpd.base import MPDClientBase
from mpd_now_playable.mpd import types

class MPDClient(MPDClientBase):
    mpd_version: str | None

    def __init__(self) -> None: ...
    async def connect(self, host: str, port: int = ...) -> None: ...
    async def password(self, password: str) -> None: ...
    def idle(self, subsystems: Sequence[str] = ...) -> AsyncIterator[Sequence[str]]: ...

    async def status(self) -> types.StatusResponse: ...
    async def currentsong(self) -> types.CurrentSongResponse: ...
    async def readpicture(self, uri: str) -> types.ReadPictureResponse: ...

    async def play(self) -> None: ...
    async def pause(self, pause: Literal[1, 0, None] = None) -> None: ...
    async def stop(self) -> None: ...
    async def next(self) -> None: ... # noqa: A003
    async def previous(self) -> None: ...
