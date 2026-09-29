# Machine Census (`machine_census`)

Weekly, read-only inventory of every VICARIUS machine that keeps agents and Lauren
installing software to the right place on both computers.

- Tags: utility | Version: 1.0.0 | Status: active | Owner: Lauren K Olinger
- Repo: `https://github.com/laurenkolinger/vicarius-machine-census` | Related studies: none

## What it does and why it exists

VICARIUS runs on two machines, vicar-mainframe and dl (the second Bizon workstation),
which have acted as one merged platform since dl joined on 2026-08-17. Machine Census
takes a weekly snapshot of each machine's packages, applications, GPUs, conda and R
environments, and desktop dock configuration, then compares the two snapshots so a
drift between them shows up on its own instead of surfacing later as a broken install.

An agent authoring or installing a module reads the resulting
`data/MACHINE_CONTEXT.md` (in this clone, at
`vicarius/modules/machine_census/github_repo/data/MACHINE_CONTEXT.md`) before choosing
where anything goes: it names the canonical install location for each kind of software
(apt, conda environments, `/opt`, `/usr/local/bin`) and lists the packages, applications
and conda environments each machine already carries. It also states the platform rule
this file exists to help authors satisfy: every module must run on all census hosts,
or its README must say why not. `report.py` writes that sentence directly, and
`module.yaml`'s `compat.rule` states the same rule on its own; neither reads from the
other. `check_module_compat.py` lets any module author check a candidate `runtime:`
block against both machines' snapshots before writing it into their own `module.yaml`,
but the rule itself is a platform convention, not something this script enforces: a
module can still be registered and run with a `runtime:` block that fails on a host.

The census changes nothing on the machine it runs on. Every probe it runs is
read-only, and a missing tool is recorded as `"absent"` rather than treated as an
error. Lauren dropped automatic Metashape version alignment from the original design
on 2026-08-17: the module reports version differences between the two machines and
leaves any upgrade decision to her.

## Where it sits in the pipeline

Machine Census sits outside the survey processing chain (`bag_metashape_export` then
`3D_phase_1` then `3D_phase2` then `reef_point_seg`). It declares no inputs and
consumes no other module's output; it reads only the machine it runs on.

Every other module is an indirect consumer of its output: an agent authoring or
installing any module reads `data/MACHINE_CONTEXT.md` first, and can run
`check_module_compat.py` against that module's own `runtime:` block to confirm both
machines satisfy it. `drive_inventory` is the platform's other `aggregate`-type module;
the two share no code or data.

## Inputs

`module.yaml` declares no inputs (`inputs: []`). The collector reads only the running
system through local commands such as `dpkg`, `snap`, `conda`, `gsettings`, `dconf`
and `nvidia-smi`. It never reads another module's output and never makes a network
call.

## Parameters

`module.yaml` declares no `parameters:` block, so the module's page on the desktop
shows no parameter fields. `collect.py` takes two command-line flags instead; see How
to run it, From the CLI.

## Outputs and data-dictionary entries

| Output dataset | Path template | What it is |
|----------------|---------------|------------|
| `machine_census_snapshot` | `github_repo/data/hosts/<hostname>/latest.json` | One machine's inventory, plus a dated copy, `census_YYYY-MM-DD.json`, beside `latest.json` on every run. |
| `machine_census_drift_report` | `github_repo/data/DRIFT_REPORT.md` | A side-by-side host comparison, a VICARIUS desktop integration table, and any stale-snapshot warnings. |
| `machine_census_context` | `github_repo/data/MACHINE_CONTEXT.md` | The install-location reference for module authors, plus each host's own facts. |

`machine_census_snapshot` holds identity, CPU and RAM, GPU, storage, apt and snap
packages, Python and conda environments, R, AI services, applications and desktop
dock state. `machine_census_drift_report` compares OS, kernel, GPU, RAM, package
counts, R and Python versions, conda environments, Ollama models, per-application
versions and paths, and the apt package-set difference, plus the VICARIUS desktop
integration table and the stale-snapshot warnings; How it works inside below
describes what each part flags. `machine_census_context` adds each host's OS, CPU,
GPU, mounts, Metashape version and Ollama models to the install-location reference.
None of the three outputs has a data-dictionary descriptor: `module.yaml` sets
`eml: false` on all three, so `_METADATA/eml/generate.py` does not run for this
module, and none of the three has a data-dictionary descriptor under
`vicarius/_METADATA/dictionary/datasets/`.

## How to run it

### From the UI

`module.yaml` declares no `ui:` block, so `/modules/machine_census` renders the
desktop's generic module-runner page (`vicarius_ui_os/templates/module.html`): the
description, a Manual link to this README, an empty input-directory field and an
empty output-directory field (the page shows both by default; module.yaml declares
no inputs and maps neither field to a script flag, so anything typed there has no
effect on the run), and a Run output console. The page renders no table of this
module's outputs and gives no way to open or view `DRIFT_REPORT.md`,
`MACHINE_CONTEXT.md` or `latest.json` from the desktop; reading a result means
opening the file on disk, since the Manual link only reproduces the outputs table
above as documentation, not a live view of the files themselves. Pressing Run or Run
in terminal on that page currently fails regardless: `module.yaml`'s `cli` block sets
`entrypoint` and `post_run`, and the desktop's job runner (`vicarius_ui_os/runner.py`)
requires a `main_script` key that this `module.yaml` does not set. The page returns
the error "module 'machine_census' has no cli.main_script defined." Use the CLI below
until that gap closes.

### From the CLI

Run the collector, then the reporter, from the clone root, with the system
interpreter's absolute path. A bare `python3` can resolve to a conda or virtual
environment instead if one is active in the shell; run `command -v python3` first and
confirm it prints `/usr/bin/python3` before shortening these commands, or invoke the
absolute path as shown, which is also what `install_schedule.sh` installs into cron
(see below):

```
cd /mnt/rip/vicarius_drive/vicarius/modules/machine_census/github_repo
/usr/bin/python3 collect.py [--out DIR] [--quiet]
/usr/bin/python3 report.py
```

`collect.py` flags:

- `--out DIR`: where to write `<hostname>/latest.json` and the dated archive.
  Defaults to `data/hosts` inside the clone.
- `--quiet`: suppress the one-line summary `collect.py` otherwise prints after
  writing the snapshot.

`report.py` takes no flags. It reads every `data/hosts/<host>/latest.json` present
(each machine ends up holding every host's snapshot once Synology Drive, the
file-sync application that mirrors `vicarius_drive` between machines, has copied it
over) and needs at least one snapshot to exist; run `collect.py` first on a machine
that has none yet.

Check a candidate module's runtime needs against both machines:

```
/usr/bin/python3 check_module_compat.py <module_dir>
```

`<module_dir>` is a module's folder, either the one holding `module.yaml` directly or
the one holding `github_repo/module.yaml`. The script prints a PASS or FAIL line per
host and exits 1 if any host fails; a module whose `module.yaml` declares no
`runtime:` block passes on every host by definition.

Install the weekly cron on the machine you run it from:

```
bash install_schedule.sh
```

`install_schedule.sh` is not marked executable in this clone, so `./install_schedule.sh`
fails with a permission error; run it with `bash` as shown, or `chmod +x` it first. The
script is idempotent (it replaces its own line on a rerun, matched by the marker
comment `# machine_census weekly`) and schedules 04:00 AST Sunday on vicar-mainframe,
04:30 AST Sunday elsewhere, so the two machines' report-writing crons never collide
inside Synology Drive. The line it installs runs the collector quietly, then the
reporter only if the collector exits zero, both through the absolute interpreter path
(cron's own PATH is minimal, so the script never relies on a bare `python3`):

```
/usr/bin/python3 collect.py --quiet && /usr/bin/python3 report.py >> census_cron.log 2>&1
```

`report.py`'s output (its `[machine_census] report over ...` success line, or any
error) is appended to `census_cron.log` beside the scripts; `collect.py` prints
nothing on success because of `--quiet`, and its own stdout and stderr are not
captured in that log.

## How it works inside

Three plain Python 3 scripts, no virtual environment or conda environment, no
third-party packages: everything comes from the standard library (`argparse`, `json`,
`re`, `subprocess`, `zoneinfo`) plus whatever system tools happen to be on the machine.

`collect.py`'s `collect()` function builds one dictionary of facts about the local
machine by shelling out to `dpkg`, `snap`, `conda`, `R`, `nvidia-smi`, `lscpu`, `free`,
`lsblk`, `df`, `ollama`, `docker` and `gsettings` (falling back to `dconf` when no
desktop session bus is available). Every shell call goes through a helper, `sh()`,
whose default timeout is 25 seconds; the one exception is the `dpkg-query` package
listing, which gets 60 seconds. `sh()` returns the command's stdout as-is regardless
of whether the command exited zero, so a failed command with no output and a missing
tool both come back as an empty string for that reason alone. `sh()` also returns an
empty string, separately, whenever the `subprocess.run` call itself raises a Python
exception rather than completing, which includes a timeout. Either way a missing
tool never crashes the run; it shows up as `"absent"` in the snapshot instead.
`main()` writes the result to `<out>/<hostname>/census_<date>.json` and
`<out>/<hostname>/latest.json`.

`report.py`'s `load_hosts()` globs every `data/hosts/*/latest.json` in the clone
(every machine ends up holding every host's snapshot because Synology Drive syncs the
whole module). `drift_report()` builds the comparison table, marking a row
`<-- DIFFERS` when the hosts disagree, except the GPU and RAM rows, which it never
marks even when they differ (the code passes `flag_diff=False` for those two rows
only, with no comment on why). It also flags any host whose `collected_at` timestamp
is more than 10 days old as a possible broken cron. It then builds the VICARIUS
desktop integration table: for each host, whether `vicarius.desktop`,
`vicar-screensaver.desktop` and `aspect-toggle.desktop` are pinned to the GNOME dock
(read from the `favorite-apps` setting via `gsettings`, falling back to `dconf read`
when no desktop session bus is available), whether the matching three launcher files
exist under `~/.local/share/applications`, and whether the
`vicarius-launchers@vicar.lab` GNOME Shell extension folder exists under
`~/.local/share/gnome-shell/extensions`. `machine_context()` builds the
install-locations reference from the first host's `conventions` block plus each
host's identity, CPU, RAM, GPU, mounts, Metashape version and Ollama models.

`check_module_compat.py` carries its own small, regex-based reader for a
`module.yaml`'s `runtime:` block (`parse_runtime()`); it does not depend on a YAML
library. `check_host()` compares that block's `binaries`, `apt`, `conda_env` and
`min_vram_mib` entries against one host's snapshot and returns a list of failure
reasons, empty when the host satisfies every requirement.

No GPU is required to run the census itself. `nvidia-smi` is one of the commands
`collect.py` probes; on a machine with no NVIDIA GPU or driver it returns nothing and
the snapshot records `"gpu": {"cards": "none", ...}`.

## Gotchas and troubleshooting

- The module page's Run and Run in terminal buttons fail with "module
  'machine_census' has no cli.main_script defined." Run `collect.py` and `report.py`
  from a terminal instead (see How to run it, From the CLI).
- `install_schedule.sh` is not executable in this clone; `./install_schedule.sh` fails
  with a permission error. Run `bash install_schedule.sh` instead.
- `report.py` exits 1 with "no snapshots found; run collect.py first" when
  `data/hosts/` holds no host folder yet.
- `check_module_compat.py` exits 1 with "no census snapshots; run collect.py" under
  the same condition.
- A "snapshot is N days old" warning in `DRIFT_REPORT.md` usually means that host's
  weekly cron stopped running, or Synology Drive has not yet copied its latest
  `latest.json` over.
- The dock-pin checks read GNOME's `favorite-apps` setting through `gsettings`,
  falling back to `dconf read` when no live desktop session bus is available (inside a
  cron job, for example). Either source can miss a pin made moments before the check
  runs, if GNOME Shell has not written it out yet.
- Conda-environment discovery only looks at `~/anaconda3/bin/conda`. A conda
  distribution installed anywhere else on a machine reports as absent.

## Resume from cold

Environment: any VICARIUS machine's system `python3` interpreter, `/usr/bin/python3`.
No venv, no conda environment, no `requirements.txt`: `collect.py` and `report.py`
need nothing beyond the Python standard library. The system tools they shell out to
(`dpkg`, `snap`, `conda`, `R`, `ollama`, `docker`, `nvidia-smi`) are each optional and
fail soft when absent.

Inputs live nowhere but the machine itself. Outputs live under this clone, at
`github_repo/data/hosts/<hostname>/` (one folder per machine, holding `latest.json`
and dated `census_YYYY-MM-DD.json` copies) and directly under `github_repo/data/`
(`DRIFT_REPORT.md`, `MACHINE_CONTEXT.md`). This module does not use the platform's
`inprocess/run_*/project.json` run-state convention: it keeps no run folders, and
`vicarius/modules/machine_census/inprocess/` stays empty.

The clone path below, `/mnt/rip/vicarius_drive/vicarius/modules/machine_census/github_repo`,
is confirmed only on vicar-mainframe. `collect.py` declares that `vicarius_drive`
mounts at the same point on both machines, as the `vicarius_platform` convention
it records and `report.py` copies into `MACHINE_CONTEXT.md`, but nothing checks
that declaration against the machine running it. Confirm it directly on the
machine you are using, rather than through a prior snapshot: a machine that has
never run the collector has no snapshot yet, which is exactly the cold-start case
below. Run
`ls /mnt/rip/vicarius_drive/vicarius/modules/machine_census/github_repo` (or, on a
different mount, find the equivalent path under wherever Synology Drive placed
`vicarius_drive` on that machine) and `command -v python3` or
`ls /usr/bin/python3`, and confirm both resolve, before running the commands below.
Once a snapshot exists for that host, its `storage.mounts` field, in
`data/hosts/<hostname>/latest.json`, also records what was mounted at the last run,
though it goes stale between weekly crons.

To run it cold on a machine that has never run it:

```
cd /mnt/rip/vicarius_drive/vicarius/modules/machine_census/github_repo
/usr/bin/python3 collect.py
/usr/bin/python3 report.py
```

Success check: after `collect.py`, `data/hosts/<hostname>/latest.json` exists and its
`collected_at` field matches the run time; `collect.py` also prints
`[machine_census] <hostname> snapshot -> <path> (<N> apt, <N> snaps)` unless run with
`--quiet`. After `report.py`, `data/DRIFT_REPORT.md` and `data/MACHINE_CONTEXT.md`
exist and open with a `Generated` or `Refreshed` line carrying the current run's
timestamp; `report.py` prints `[machine_census] report over <N> host(s): <names> ->
data/DRIFT_REPORT.md, data/MACHINE_CONTEXT.md` on success.

## Provenance and links

- Repo: `https://github.com/laurenkolinger/vicarius-machine-census`
- Related studies: none. This is a platform utility, not a TCRMP study tool.
- Related modules: none directly. Every module author is an indirect reader of
  `data/MACHINE_CONTEXT.md`, and any module can run `check_module_compat.py` against
  its own `runtime:` block.
- Data-dictionary descriptors: none. This module owns no descriptor under
  `vicarius/_METADATA/dictionary/datasets/`.
