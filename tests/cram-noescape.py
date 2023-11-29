#!/usr/bin/env python3

import runpy

import cram  # type: ignore [import]

cram._test._needescape = lambda _: False
runpy.run_module('cram')
