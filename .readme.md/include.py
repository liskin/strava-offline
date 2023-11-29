#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import re
from sys import stdin
from sys import stdout


def include(m: re.Match[str]) -> str:
    f = Path(m[1]).read_text()
    return f"<!-- include {m[1]} -->\n{f}<!-- end include -->"


def includes(s: str) -> str:
    return re.sub(r"(?s)<!-- include (\S+) .*? end include -->", include, s)


if __name__ == "__main__":
    stdout.write(includes(stdin.read()))
