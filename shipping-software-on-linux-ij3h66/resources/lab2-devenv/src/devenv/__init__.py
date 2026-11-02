"""devenv: a tiny developer CLI for the course labs."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("shiplab-devenv")
except PackageNotFoundError:  # running from a source tree that was never installed
    __version__ = "0+unknown"
