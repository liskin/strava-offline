# strava-offline

[![PyPI Python Version badge](https://img.shields.io/pypi/pyversions/strava-offline)](https://pypi.org/project/strava-offline/)
[![PyPI Version badge](https://img.shields.io/pypi/v/strava-offline)](https://pypi.org/project/strava-offline/)
![License badge](https://img.shields.io/github/license/liskin/strava-offline)

## Overview

strava-offline is a …

<!-- FIXME: example image -->

## Installation

Using [pipx][]:

```
pipx ensurepath
pipx install strava-offline
```

To keep a local git clone around:

```
git clone https://github.com/liskin/strava-offline
make -C strava-offline pipx
```

Alternatively, if you don't need the isolated virtualenv that [pipx][]
provides, feel free to just:

```
pip install strava-offline
```

[pipx]: https://github.com/pypa/pipx

## Usage

<!-- include .readme.md/help.md -->
    $ strava-offline --help
    Usage: strava-offline [OPTIONS]
    
    Options:
      --config FILE    Read configuration from FILE.  [default:
                       /home/user/.config/strava_offline/config.yaml]
      --config-sample  Show sample configuration file
      --help           Show this message and exit.
<!-- end include -->

<!-- FIXME: example -->

### Configuration file

Secrets (and other options) can be set permanently in a config file,
which is located at `~/.config/strava_offline/config.yaml` by default
(on Linux; on other platforms see output of `--help`).

Sample config file can be generated using the `--config-sample` flag:

<!-- include .readme.md/config-sample.md -->
    $ strava-offline --config-sample
<!-- end include -->

## Donations (♥ = €)

If you like this tool and wish to support its development and maintenance,
please consider [a small donation](https://www.paypal.me/lisknisi/10EUR) or
[recurrent support through GitHub Sponsors](https://github.com/sponsors/liskin).

By donating, you'll also support the development of my other projects. You
might like these:

* <!-- FIXME: [name](link) --> – <!-- FIXME: description -->
