from dataclasses import dataclass


@dataclass(slots=True)
class Queue:
	#: The zero-based index of the current song in MPD's queue.
	current: int
	#: The index of the next song to be played, taking into account random and
	#: repeat playback settings.
	next: int
	#: The total length of MPD's queue - the last song in the queue will have
	#: the index one less than this, since queue indices are zero-based.
	length: int
