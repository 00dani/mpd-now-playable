import argparse
import asyncio
import sys
from collections.abc import Iterable

from rich import print as rich_print

from .__version__ import __version__
from .config.load import loadConfig
from .config.model import Config
from .launchd import DEFAULT_LABEL, install_launchagent, uninstall_launchagent
from .mpd.listener import MpdStateListener
from .song_receiver import (
	Receiver,
	choose_loop_factory,
	construct_receiver,
)


async def listen(
	config: Config, listener: MpdStateListener, receivers: Iterable[Receiver]
) -> None:
	await listener.start(config.mpd)
	await asyncio.gather(*(rec.start(listener) for rec in receivers))
	await listener.loop(receivers)


def print_help() -> None:
	parser = build_parser()
	parser.print_help()


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(prog="mpd-now-playable")
	parser.add_argument(
		"-v",
		"--version",
		action="store_true",
		help="Show version and exit.",
	)

	subparsers = parser.add_subparsers(dest="command")
	install_cmd = subparsers.add_parser(
		"install-launchagent",
		help="Install and start a per-user launchd service.",
	)
	install_cmd.add_argument(
		"--label",
		default=DEFAULT_LABEL,
		help=f"launchd label to install (default: {DEFAULT_LABEL}).",
	)
	install_cmd.add_argument(
		"--force",
		action="store_true",
		help="Replace an existing plist with the same label.",
	)

	uninstall_cmd = subparsers.add_parser(
		"uninstall-launchagent",
		help="Unload and remove a per-user launchd service.",
	)
	uninstall_cmd.add_argument(
		"--label",
		default=DEFAULT_LABEL,
		help=f"launchd label to uninstall (default: {DEFAULT_LABEL}).",
	)
	return parser


def main() -> None:
	parser = build_parser()
	args = parser.parse_args(sys.argv[1:])

	if args.version:
		rich_print(f"mpd-now-playable v{__version__}")
		return

	if args.command == "install-launchagent":
		path = install_launchagent(label=args.label, force=args.force)
		rich_print(f"Installed LaunchAgent at {path}")
		return

	if args.command == "uninstall-launchagent":
		path = uninstall_launchagent(label=args.label)
		rich_print(f"Uninstalled LaunchAgent at {path}")
		return

	rich_print(f"mpd-now-playable v{__version__}")
	config = loadConfig()
	rich_print(config)

	listener = MpdStateListener(config.cache)
	receivers = tuple(construct_receiver(rec_config) for rec_config in config.receivers)
	factory = choose_loop_factory(receivers)

	asyncio.run(
		listen(config, listener, receivers),
		loop_factory=factory.make_loop,
		debug=False,
	)


if __name__ == "__main__":
	main()
