#!/usr/bin/env bash

set -eu -o pipefail

make

. ./.private.sh
./.venv/bin/strava-offline "$@"
