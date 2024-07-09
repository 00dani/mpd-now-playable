from asyncio import AbstractEventLoop, new_event_loop
from dataclasses import dataclass
from importlib import import_module
from typing import Generic, Iterable, Literal, Protocol, TypeVar, cast

from .config.model import BaseReceiverConfig, Config
from .player import Player
from .song import Song
from .tools.types import not_none

T = TypeVar("T", bound=AbstractEventLoop, covariant=True)


class LoopFactory(Generic[T], Protocol):
	@property
	def is_replaceable(self) -> bool: ...

	@classmethod
	def make_loop(cls) -> T: ...


class Receiver(Protocol):
	def __init__(self, player: Player, config: Config) -> None: ...
	@classmethod
	def loop_factory(cls) -> LoopFactory[AbstractEventLoop]: ...
	def update(self, song: Song | None) -> None: ...


class ReceiverModule(Protocol):
	receiver: type[Receiver]


class DefaultLoopFactory(LoopFactory[AbstractEventLoop]):
	@property
	def is_replaceable(self) -> Literal[True]:
		return True

	@classmethod
	def make_loop(cls) -> AbstractEventLoop:
		return new_event_loop()


@dataclass
class IncompatibleReceiverError(Exception):
	a: type[Receiver]
	b: type[Receiver]


def import_receiver(config: BaseReceiverConfig) -> type[Receiver]:
	mod = cast(
		ReceiverModule, import_module(f"mpd_now_playable.receivers.{config.kind}")
	)
	return mod.receiver


def choose_loop_factory(
	receivers: Iterable[type[Receiver]],
) -> LoopFactory[AbstractEventLoop]:
	"""Given the desired receivers, determine which asyncio event loop implementation will support all of them. Will raise an IncompatibleReceiverError if no such implementation exists."""

	chosen_fac: LoopFactory[AbstractEventLoop] = DefaultLoopFactory()
	chosen_rec: type[Receiver] | None = None

	for rec in receivers:
		fac = rec.loop_factory()
		if fac.is_replaceable:
			continue

		if chosen_fac.is_replaceable:
			chosen_fac = fac
		elif type(fac) is not type(chosen_fac):
			raise IncompatibleReceiverError(rec, not_none(chosen_rec))

		chosen_rec = rec

	return chosen_fac
