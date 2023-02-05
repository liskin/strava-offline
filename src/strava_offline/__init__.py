# type: ignore

import sys

if sys.version_info >= (3, 10):
    import importlib.metadata as importlib_metadata  # isort: skip
else:
    import importlib_metadata  # isort: skip

try:
    __version__ = importlib_metadata.version(__name__)
except importlib_metadata.PackageNotFoundError:
    # package is not installed
    pass
