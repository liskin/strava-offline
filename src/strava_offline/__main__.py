# type: ignore

import importlib.metadata
import sys

if __name__ == "__main__":
    _name = importlib.metadata.distribution(__package__).name
    (_script,) = importlib.metadata.entry_points(group='console_scripts', name=_name)
    _main = _script.load()
    sys.exit(_main())
