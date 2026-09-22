# Machine Census

Weekly read-only inventory of every VICARIUS machine, the drift report between
them, and the canonical machine context for agents. Built 2026-08-17 when dl
(the second Bizon box) joined vicar-mainframe as one merged platform.

## What runs where

- `collect.py` runs on EACH machine (weekly cron; also on demand) and writes
  `data/hosts/<hostname>/latest.json` + a dated archive. Read-only: it never
  installs, never modifies system state.
- Synology Drive syncs the whole module (it lives inside vicarius_drive), so
  each machine ends up holding every host's snapshot.
- `report.py` renders `data/DRIFT_REPORT.md` (side-by-side versions, package-set
  deltas, dock-integration checks, stale-snapshot warnings) and
  `data/MACHINE_CONTEXT.md` (canonical install locations + per-host facts).
- `check_module_compat.py <module_dir>` validates a module.yaml `runtime:`
  block against every host's snapshot: the runs-on-both-machines gate.
- `install_schedule.sh` installs the weekly cron on the invoking machine
  (Sun 04:00 AST on vicar-mainframe, 04:30 elsewhere to avoid report-write
  collisions in Synology).

## The rule this module enforces

The machines are one platform. Every module must run on all census hosts, or
its README must say why not. Agents: read `data/MACHINE_CONTEXT.md` before
installing anything; it lists where things go (apt / conda envs / /opt /
/usr/local/bin) and what each host has. The vicarius CLAUDE.md points here.

## Desktop integration checks

The census verifies on each host that the VICARIUS dock icons (vicarius,
vicar-screensaver, aspect-toggle) are pinned, their launcher files exist, and
the vicarius-launchers GNOME extension is present; drift shows in the report.
