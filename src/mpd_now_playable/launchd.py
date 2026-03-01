import os
import plistlib
import subprocess
import sys
from pathlib import Path

DEFAULT_LABEL = "me.00dani.mpd-now-playable"


def _require_macos() -> None:
	if sys.platform != "darwin":
		msg = "launchd commands are only supported on macOS"
		raise RuntimeError(msg)


def _launch_agents_dir() -> Path:
	return Path.home() / "Library" / "LaunchAgents"


def plist_path_for_label(label: str) -> Path:
	return _launch_agents_dir() / f"{label}.plist"


def _service_target(label: str) -> str:
	return f"gui/{os.getuid()}/{label}"


def _launchctl_binary() -> str:
	# Prefer absolute paths to avoid relying on PATH for privileged process control.
	for candidate in ("/bin/launchctl", "/usr/bin/launchctl"):
		if Path(candidate).exists():
			return candidate
	return "launchctl"


def _run_launchctl(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
	return subprocess.run(  # noqa: S603 - arguments are fixed command tokens, shell is not used.
		[_launchctl_binary(), *args],
		check=check,
		capture_output=True,
		text=True,
	)


def _plist_bytes(label: str) -> bytes:
	payload = {
		"Label": label,
		"ProgramArguments": [sys.executable, "-m", "mpd_now_playable.cli"],
		"RunAtLoad": True,
		"KeepAlive": True,
	}
	return plistlib.dumps(payload, fmt=plistlib.FMT_XML)


def install_launchagent(label: str = DEFAULT_LABEL, force: bool = False) -> Path:
	_require_macos()
	plist_path = plist_path_for_label(label)
	plist_path.parent.mkdir(parents=True, exist_ok=True)

	if plist_path.exists() and not force:
		msg = f"{plist_path} already exists; rerun with --force to replace it"
		raise FileExistsError(msg)

	plist_path.write_bytes(_plist_bytes(label))
	target = _service_target(label)

	# Ignore errors if the service does not already exist.
	_run_launchctl("bootout", target, check=False)
	_run_launchctl("bootstrap", f"gui/{os.getuid()}", str(plist_path))
	_run_launchctl("kickstart", "-k", target)

	return plist_path


def uninstall_launchagent(label: str = DEFAULT_LABEL) -> Path:
	_require_macos()
	plist_path = plist_path_for_label(label)
	target = _service_target(label)

	# Ignore errors if the service is not loaded.
	_run_launchctl("bootout", target, check=False)
	if plist_path.exists():
		plist_path.unlink()

	return plist_path
