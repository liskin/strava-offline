# type: ignore

import sys

if sys.version_info >= (3, 10):
    import importlib.metadata as importlib_metadata  # isort: skip
else:
    import importlib_metadata  # isort: skip

if __name__ == "__main__":
    _name = importlib_metadata.distribution(__package__).name
    (_script,) = importlib_metadata.entry_points(group='console_scripts', name=_name)
    _main = _script.load()
    sys.exit(_main())
