from types import SimpleNamespace

import mpd_now_playable.cli as cli


def test_main_help_prints_usage(monkeypatch, capsys) -> None:
	monkeypatch.setattr(cli.sys, "argv", ["mpd-now-playable", "--help"])

	def fail_load() -> None:
		raise AssertionError("loadConfig should not run for --help")

	monkeypatch.setattr(cli, "loadConfig", fail_load)

	cli.main()
	output = capsys.readouterr().out

	assert "Usage: mpd-now-playable [OPTIONS]" in output
	assert "-h, --help" in output
	assert "-v, --version" in output


def test_main_version_prints_version(monkeypatch, capsys) -> None:
	monkeypatch.setattr(cli.sys, "argv", ["mpd-now-playable", "--version"])

	def fail_load() -> None:
		raise AssertionError("loadConfig should not run for --version")

	monkeypatch.setattr(cli, "loadConfig", fail_load)

	cli.main()
	output = capsys.readouterr().out

	assert output.strip() == f"mpd-now-playable v{cli.__version__}"


def test_main_starts_listener_and_receivers(monkeypatch) -> None:
	receiver_cfg_1 = SimpleNamespace(kind="websockets")
	receiver_cfg_2 = SimpleNamespace(kind="websockets")
	config = SimpleNamespace(
		cache="memory://",
		mpd=SimpleNamespace(host="127.0.0.1", port=6600),
		receivers=(receiver_cfg_1, receiver_cfg_2),
	)

	listener = object()
	receiver_1 = object()
	receiver_2 = object()
	fake_coroutine = object()

	seen = {}

	def fake_load_config() -> SimpleNamespace:
		return config

	def fake_listener_ctor(cache: str) -> object:
		seen["cache"] = cache
		return listener

	def fake_construct_receiver(rcfg: SimpleNamespace) -> object:
		if rcfg is receiver_cfg_1:
			return receiver_1
		if rcfg is receiver_cfg_2:
			return receiver_2
		raise AssertionError(f"Unexpected receiver config: {rcfg!r}")

	class FakeLoopFactory:
		@staticmethod
		def make_loop() -> object:
			return object()

	def fake_choose_loop_factory(receivers: tuple[object, ...]) -> type[FakeLoopFactory]:
		seen["receivers"] = receivers
		return FakeLoopFactory

	def fake_listen(cfg: SimpleNamespace, lst: object, receivers: tuple[object, ...]) -> object:
		seen["listen_args"] = (cfg, lst, receivers)
		return fake_coroutine

	def fake_run(coro: object, *, loop_factory: object, debug: bool) -> None:
		seen["run"] = (coro, loop_factory, debug)

	monkeypatch.setattr(cli.sys, "argv", ["mpd-now-playable"])
	monkeypatch.setattr(cli, "loadConfig", fake_load_config)
	monkeypatch.setattr(cli, "MpdStateListener", fake_listener_ctor)
	monkeypatch.setattr(cli, "construct_receiver", fake_construct_receiver)
	monkeypatch.setattr(cli, "choose_loop_factory", fake_choose_loop_factory)
	monkeypatch.setattr(cli, "listen", fake_listen)
	monkeypatch.setattr(cli.asyncio, "run", fake_run)

	cli.main()

	assert seen["cache"] == "memory://"
	assert seen["receivers"] == (receiver_1, receiver_2)
	assert seen["listen_args"] == (config, listener, (receiver_1, receiver_2))
	assert seen["run"] == (fake_coroutine, FakeLoopFactory.make_loop, False)
