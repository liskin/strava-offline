#!/usr/bin/env python3

from pathlib import Path
import runpy

import prysk.test  # type: ignore [import]

prysk.test._IS_ESCAPING_NEEDED = lambda _: False
prysk.test._findtests = lambda paths: map(Path, paths)  # https://github.com/prysk/prysk/issues/224
runpy.run_module('prysk')
