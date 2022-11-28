try:
    from importlib.metadata import version, PackageNotFoundError  # type: ignore # isort: skip
except ImportError:
    from importlib_metadata import version, PackageNotFoundError  # type: ignore # isort: skip

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # package is not installed
    pass
