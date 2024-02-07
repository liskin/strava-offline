#!/usr/bin/env python3

import runpy

import prysk.test  # type: ignore [import]

prysk.test._IS_ESCAPING_NEEDED = lambda _: False
runpy.run_module('prysk')
