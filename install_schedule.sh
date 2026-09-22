#!/usr/bin/env bash
# Idempotent weekly-census cron install for THIS machine. vicar-mainframe runs
# at 04:00 Sunday (after the 03:00 NAS drive-inventory sync); every other host
# runs at 04:30 so the two report writers never collide inside Synology Drive.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
MARK="# machine_census weekly"
[[ "$(hostname)" == "vicar-mainframe" ]] && MIN_HR="0 4" || MIN_HR="30 4"
LINE="$MIN_HR * * 0 /usr/bin/python3 $HERE/collect.py --quiet && /usr/bin/python3 $HERE/report.py >> $HERE/census_cron.log 2>&1 $MARK"
( crontab -l 2>/dev/null | grep -vF "$MARK"; echo "$LINE" ) | crontab -
echo "[machine_census] weekly cron installed on $(hostname): $(crontab -l | grep -F "$MARK")"
