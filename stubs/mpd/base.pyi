from enum import Enum

class FailureResponseCode(Enum):
    NOT_LIST: int
    ARG: int
    PASSWORD: int
    PERMISSION: int
    UNKNOWN: int
    NO_EXIST: int
    PLAYLIST_MAX: int
    SYSTEM: int
    PLAYLIST_LOAD: int
    UPDATE_ALREADY: int
    PLAYER_SYNC: int
    EXIST: int

class MPDError(Exception): ...

class CommandError(MPDError):
    pass

class MPDClientBase:
    pass
