#!/usr/bin/env python3
"""Validate a module's runtime needs against every census host.

Usage: python3 check_module_compat.py <module_dir>

Reads the module's module.yaml optional `runtime:` block:

    runtime:
      binaries: [ffmpeg, docker]        # must exist on PATH facts
      apt: [libgdal-dev]                # must be in the host's apt map
      conda_env: vicarius-tagfab        # named env must exist
      min_vram_mib: 24000               # each host needs one GPU this large

Prints a per-host PASS/FAIL table; exits 1 on any FAIL. A module with no
runtime block passes everywhere by definition (stdlib-only assumption).
"""
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def parse_runtime(module_yaml_path):
    """Tiny purpose-built parser: pulls the runtime: block without needing pyyaml."""
    txt = open(module_yaml_path).read()
    m = re.search(r"^runtime:\s*\n((?:[ \t]+.*\n?)*)", txt, re.M)
    if not m:
        return {}
    block, rt = m.group(1), {}
    for key in ("binaries", "apt"):
        k = re.search(rf"^\s+{key}:\s*\[([^\]]*)\]", block, re.M)
        if k:
            rt[key] = [x.strip().strip("'\"") for x in k.group(1).split(",") if x.strip()]
    k = re.search(r"^\s+conda_env:\s*(\S+)", block, re.M)
    if k:
        rt["conda_env"] = k.group(1).strip("'\"")
    k = re.search(r"^\s+min_vram_mib:\s*(\d+)", block, re.M)
    if k:
        rt["min_vram_mib"] = int(k.group(1))
    return rt


def check_host(rt, snap):
    fails = []
    apt = snap["packages"]["apt"]
    for b in rt.get("binaries", []):
        known = {a["name"]: a for a in snap["apps"].values()}
        if b in known and known[b]["path"] != "absent":
            continue
        if not any(p == b or p.startswith(b) for p in apt):
            fails.append(f"binary/pkg '{b}' not found")
    for p in rt.get("apt", []):
        if p not in apt:
            fails.append(f"apt '{p}' missing")
    env = rt.get("conda_env")
    if env and env not in snap["python"]["conda_envs"]:
        fails.append(f"conda env '{env}' missing")
    need = rt.get("min_vram_mib")
    if need:
        vrams = [int(x) for x in re.findall(r"(\d+)\s*MiB", snap["gpu"]["cards"])]
        if not vrams or max(vrams) < need:
            fails.append(f"needs {need} MiB VRAM; host max {max(vrams) if vrams else 0}")
    return fails


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    mod = sys.argv[1]
    yml = os.path.join(mod, "module.yaml")
    if not os.path.exists(yml):
        yml = os.path.join(mod, "github_repo", "module.yaml")
    if not os.path.exists(yml):
        print(f"FAIL: no module.yaml under {mod}")
        return 1
    rt = parse_runtime(yml)
    snaps = {json.load(open(p))["hostname"]: json.load(open(p))
             for p in glob.glob(os.path.join(HERE, "data", "hosts", "*", "latest.json"))}
    if not snaps:
        print("FAIL: no census snapshots; run collect.py")
        return 1
    if not rt:
        print(f"{os.path.basename(os.path.abspath(mod))}: no runtime block; PASS on all hosts by definition"
              f" ({', '.join(snaps)})")
        return 0
    bad = 0
    print(f"module: {os.path.basename(os.path.abspath(mod))}  runtime: {rt}")
    for h, snap in sorted(snaps.items()):
        fails = check_host(rt, snap)
        print(f"  {h:<18} {'PASS' if not fails else 'FAIL: ' + '; '.join(fails)}")
        bad += bool(fails)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
