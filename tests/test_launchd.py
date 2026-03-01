import plistlib
from pathlib import Path

import pytest

import mpd_now_playable.launchd as launchd


def test_plist_bytes_uses_absolute_python(monkeypatch, tmp_path) -> None:
	monkeypatch.setattr(launchd.sys, "executable", "/abs/python")
	monkeypatch.setattr(Path, "home", lambda: tmp_path)

	payload = plistlib.loads(launchd._plist_bytes("com.example.test"))

	assert payload["Label"] == "com.example.test"
	assert payload["ProgramArguments"] == ["/abs/python", "-m", "mpd_now_playable.cli"]
	assert payload["RunAtLoad"] is True
	assert payload["KeepAlive"] is True


def test_install_launchagent_writes_plist_and_bootstraps(monkeypatch, tmp_path) -> None:
	monkeypatch.setattr(launchd.sys, "platform", "darwin")
	monkeypatch.setattr(launchd.sys, "executable", "/abs/python")
	monkeypatch.setattr(Path, "home", lambda: tmp_path)
	monkeypatch.setattr(launchd.os, "getuid", lambda: 501)

	seen: list[tuple[tuple[str, ...], bool]] = []

	def fake_run_launchctl(*args: str, check: bool = True) -> object:
		seen.append((args, check))
		return object()

	monkeypatch.setattr(launchd, "_run_launchctl", fake_run_launchctl)

	plist_path = launchd.install_launchagent(label="com.example.test", force=False)
	assert plist_path == tmp_path / "Library" / "LaunchAgents" / "com.example.test.plist"
	assert plist_path.exists()
	assert seen == [
		(("bootout", "gui/501/com.example.test"), False),
		(("bootstrap", "gui/501", str(plist_path)), True),
		(("kickstart", "-k", "gui/501/com.example.test"), True),
	]


def test_install_launchagent_refuses_existing_without_force(monkeypatch, tmp_path) -> None:
	monkeypatch.setattr(launchd.sys, "platform", "darwin")
	monkeypatch.setattr(Path, "home", lambda: tmp_path)

	plist = tmp_path / "Library" / "LaunchAgents" / "com.example.test.plist"
	plist.parent.mkdir(parents=True, exist_ok=True)
	plist.write_text("already here")

	with pytest.raises(FileExistsError):
		launchd.install_launchagent(label="com.example.test")


def test_uninstall_launchagent_boots_out_and_removes_file(monkeypatch, tmp_path) -> None:
	monkeypatch.setattr(launchd.sys, "platform", "darwin")
	monkeypatch.setattr(Path, "home", lambda: tmp_path)
	monkeypatch.setattr(launchd.os, "getuid", lambda: 501)

	seen: list[tuple[tuple[str, ...], bool]] = []

	def fake_run_launchctl(*args: str, check: bool = True) -> object:
		seen.append((args, check))
		return object()

	monkeypatch.setattr(launchd, "_run_launchctl", fake_run_launchctl)

	plist = tmp_path / "Library" / "LaunchAgents" / "com.example.test.plist"
	plist.parent.mkdir(parents=True, exist_ok=True)
	plist.write_text("x")

	removed = launchd.uninstall_launchagent(label="com.example.test")
	assert removed == plist
	assert not plist.exists()
	assert seen == [(("bootout", "gui/501/com.example.test"), False)]
