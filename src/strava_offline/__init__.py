try:
    import importlib.metadata as importlib_metadata  # type: ignore # isort: skip
except ImportError:
    import importlib_metadata  # type: ignore # isort: skip

try:
    __version__ = importlib_metadata.version(__name__)
except importlib_metadata.PackageNotFoundError:
    # package is not installed
    pass
