# mpd-now-playable [![PyPI version](https://badge.fury.io/py/mpd-now-playable.svg)](https://badge.fury.io/py/mpd-now-playable)

This little Python program turns your MPD server into a [now playable app](https://developer.apple.com/documentation/mediaplayer/becoming_a_now_playable_app) on MacOS.
This enables your keyboard's standard media keys to control MPD, as well as more esoteric music control methods like the buttons on your Bluetooth headphones.

## Installation

The recommended way to install mpd-now-playable and its dependencies is with [pipx](https://pypa.github.io/pipx/):
```shell
pipx install mpd-now-playable
```

Once pipx is done, the `mpd-now-playable` script should be available on your `$PATH` and ready to use.

Most likely, you'll want mpd-now-playable to stay running in the background as a launchd service. [Here's the service plist I use](https://git.00dani.me/00dani/mpd-now-playable/src/branch/main/me.00dani.mpd-now-playable.plist), but it's hardcoded to my `$HOME` so you'll want to customise it.

## Configuration

You may not need any configuration! If you've got a relatively normal MPD setup on your local machine, mpd-now-playable ought to just work out of the box, as it uses sensible defaults. If you need to control a remote MPD server, or your MPD clients use a password, though, you'll need configuration for that use case.

Currently, mpd-now-playable can only be configured through environment variables. Command-line arguments are intentionally not supported, since your MPD password is among the supported settings and command-line arguments are not a secure way to pass secrets such as passwords into commands. Reading configuration from a file is secure, so mpd-now-playable may support a config file in future.

The following environment variables are read. The `MPD_HOST` and `MPD_PORT` variables are supported in the same way `mpc` uses them, but you can alternatively provide your password as a separate `MPD_PASSWORD` variable if you wish.

- `MPD_HOST` - defaults to `localhost`, which should be fine for most users. If you want to control a remote MPD server, though, you can.
- `MPD_PORT` - defaults to 6600, which will almost always be the correct port to use.
- `MPD_PASSWORD` - has no default. Set this only if your MPD server expects a password. You can also provide a password by setting `MPD_HOST=password@host`, if you want to be consistent with how `mpc` works.

One simple secure way to set your environment variables is with a small wrapper script like this:
```shell
#!/bin/sh
export MPD_HOSTNAME=my.cool.mpd.host
export MPD_PORT=6700
export MPD_PASSWORD=swordfish
exec mpd-now-playable
```
Make sure this wrapper script is only readable by you, with something like `chmod 700`!

## Limitations

mpd-now-playable is currently *very* specific to MacOS. I did my best to keep the generic MPD and extremely Apple parts separate, but it definitely won't work with MPRIS2 or the Windows system media feature.

Chances are my MacOS integration code isn't the best, either. This is the first project I've written using PyObjC and it took a lot of fiddling to get working.

I'm very open to contributions to fix any of these things, if you're interested in writing them!
