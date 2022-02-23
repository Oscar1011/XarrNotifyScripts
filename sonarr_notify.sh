#!/bin/sh
BASE_ROOT=$(cd "$(dirname "$0")";pwd)
python3 "${BASE_ROOT}/sonarr_notify.py"
