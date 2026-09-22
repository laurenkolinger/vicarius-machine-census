#!/usr/bin/env python3
"""Machine Census collector: read-only hardware/software inventory of THIS machine.

Writes data/hosts/<hostname>/census_<date>.json and latest.json. Runs on any
VICARIUS machine with python3 stdlib alone; every probe is optional and fails
soft so a missing tool yields "absent", never a crash. Synology Drive syncs the
per-host snapshots between machines; report.py renders the combined drift view.
"""
import argparse, json, os, re, subprocess, sys
from datetime import datetime
from zoneinfo import ZoneInfo

SCHEMA_VERSION = "1.0.0"
AST = ZoneInfo("America/St_Thomas")


def sh(cmd, timeout=25):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return ""


def ver_of(cmd, pattern=r"([0-9]+\.[0-9][0-9a-z.\-]*)"):
    out = sh(cmd)
    m = re.search(pattern, out)
    return m.group(1) if m else (out.splitlines()[0][:60] if out else "absent")


def app_entry(name, path_cmd, version_cmd):
    path = sh(path_cmd)
    return {"name": name, "path": path or "absent",
            "version": ver_of(version_cmd) if path else "absent"}


def collect():
    host = sh("hostname")
    d = {"schema_version": SCHEMA_VERSION, "hostname": host,
         "collected_at": datetime.now(AST).strftime("%Y-%m-%d %H:%M AST")}

    d["identity"] = {
        "os": sh(". /etc/os-release && echo $PRETTY_NAME"),
        "kernel": sh("uname -r"),
        "model": sh("cat /sys/devices/virtual/dmi/id/product_name 2>/dev/null"),
        "vendor": sh("cat /sys/devices/virtual/dmi/id/sys_vendor 2>/dev/null"),
    }
    d["cpu_ram"] = {
        "cpu": sh("lscpu | awk -F': +' '/Model name/{print $2}' | head -1"),
        "threads": sh("nproc"),
        "ram": sh("free -h | awk '/^Mem:/{print $2}'"),
    }
    d["gpu"] = {
        "cards": sh("nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader") or "none",
        "cuda_apt": sh("dpkg -l | awk '/^ii +cuda-toolkit-1/{print $2\" \"$3}' | head -3"),
    }
    d["storage"] = {
        "disks": sh("lsblk -dno NAME,SIZE,MODEL | grep -v loop"),
        "mounts": sh("df -h --output=target,size,used,avail -x tmpfs -x devtmpfs -x squashfs -x efivarfs -x overlay | tail -n +2"),
    }
    d["packages"] = {
        "apt_count": int(sh("dpkg -l | grep -c '^ii'") or 0),
        "apt": dict(l.split("\t") for l in sh("dpkg-query -W -f '${Package}\\t${Version}\\n'", 60).splitlines() if "\t" in l),
        "snaps": dict((p[0], p[1]) for l in sh("snap list 2>/dev/null | tail -n +2").splitlines() if (p := l.split()) and len(p) > 1),
    }
    conda = os.path.expanduser("~/anaconda3/bin/conda")
    envs = [l.split()[0] for l in sh(f"{conda} env list 2>/dev/null").splitlines()
            if l and not l.startswith("#") and l.split() and l.split()[0] not in ("",)]
    d["python"] = {
        "system_python3": ver_of("/usr/bin/python3 --version"),
        "anaconda_present": os.path.isdir(os.path.expanduser("~/anaconda3")),
        "conda_envs": {e: ver_of(f"{conda} run -n {e} python --version 2>/dev/null", r"([0-9.]+)") for e in envs if e != "base"} if envs else {},
    }
    d["r"] = {
        "version": ver_of("R --version 2>/dev/null | head -1"),
        "user_lib_packages": int(sh("ls ~/R/*/[0-9]* 2>/dev/null | wc -l") or 0) or int(sh("find ~/R -maxdepth 3 -mindepth 3 -type d 2>/dev/null | wc -l") or 0),
    }
    d["services_ai"] = {
        "ollama_models": sh("ollama list 2>/dev/null | tail -n +2 | awk '{print $1\" \"$3\" \"$4}'") or "none",
        "docker_images": sh("docker images --format '{{.Repository}}:{{.Tag}}' 2>/dev/null | grep -v '<none>'").splitlines(),
    }
    d["apps"] = {a["name"]: a for a in [
        app_entry("metashape", "ls -d /opt/metashape-pro 2>/dev/null", "/opt/metashape-pro/metashape.sh --version 2>/dev/null"),
        app_entry("claude_code", "command -v claude || ls ~/.local/bin/claude 2>/dev/null || ls ~/.npm-global/bin/claude 2>/dev/null",
                  "claude --version 2>/dev/null || ~/.local/bin/claude --version 2>/dev/null"),
        app_entry("node", "command -v node", "node --version 2>/dev/null"),
        app_entry("gh", "command -v gh", "gh --version 2>/dev/null | head -1"),
        app_entry("ffmpeg", "command -v ffmpeg", "ffmpeg -version 2>/dev/null | head -1"),
        app_entry("ollama", "command -v ollama", "ollama --version 2>/dev/null"),
        app_entry("docker", "command -v docker", "docker --version 2>/dev/null"),
        app_entry("synology_drive", "ls -d /opt/Synology/SynologyDrive 2>/dev/null || dpkg -l synology-drive 2>/dev/null | awk '/^ii/{print \"dpkg\"}'", "dpkg-query -W -f '${Version}' synology-drive 2>/dev/null"),
        app_entry("splashtop", "dpkg -l splashtop-streamer 2>/dev/null | awk '/^ii/{print \"dpkg\"}'", "dpkg-query -W -f '${Version}' splashtop-streamer 2>/dev/null"),
    ]}
    bus = f"unix:path=/run/user/{os.getuid()}/bus"
    favs = sh(f"DBUS_SESSION_BUS_ADDRESS={bus} gsettings get org.gnome.shell favorite-apps 2>/dev/null") \
        or sh("dconf read /org/gnome/shell/favorite-apps 2>/dev/null")
    launchers = os.path.expanduser("~/.local/share/applications")
    d["desktop"] = {
        "dock_favorites": favs,
        "vicarius_pinned": "vicarius.desktop" in favs,
        "screensaver_pinned": "vicar-screensaver.desktop" in favs,
        "aspect_toggle_pinned": "aspect-toggle.desktop" in favs,
        "launcher_files_present": {f: os.path.exists(os.path.join(launchers, f))
                                   for f in ("vicarius.desktop", "vicar-screensaver.desktop", "aspect-toggle.desktop")},
        "vicarius_extension_present": os.path.isdir(os.path.expanduser(
            "~/.local/share/gnome-shell/extensions/vicarius-launchers@vicar.lab")),
    }
    d["conventions"] = {
        "system_libraries": "apt (never pip --user for system tools)",
        "python_envs": "/home/bizon/anaconda3/envs/<env> (conda); per-module venvs live inside the module's github_repo",
        "vendor_apps": "/opt/<vendor> (metashape-pro, Synology, bizon_monitoring)",
        "single_binaries": "/usr/local/bin (ollama)",
        "r_packages": "~/R user library via CRAN/r2u apt where possible",
        "vicarius_platform": "/mnt/rip/vicarius_drive/vicarius (Synology-synced; BOTH machines)",
        "never": "no installs into /usr/lib by hand, no sudo pip, no second conda distribution",
    }
    return d


def main():
    ap = argparse.ArgumentParser(description="Machine Census read-only collector")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "hosts"),
                    help="hosts output dir (default: module data/hosts)")
    ap.add_argument("--quiet", action="store_true", help="suppress summary line")
    a = ap.parse_args()
    d = collect()
    host_dir = os.path.join(a.out, d["hostname"])
    os.makedirs(host_dir, exist_ok=True)
    dated = os.path.join(host_dir, f"census_{datetime.now(AST).strftime('%Y-%m-%d')}.json")
    for p in (dated, os.path.join(host_dir, "latest.json")):
        with open(p, "w") as f:
            json.dump(d, f, indent=1)
    if not a.quiet:
        print(f"[machine_census] {d['hostname']} snapshot -> {dated} "
              f"({d['packages']['apt_count']} apt, {len(d['packages']['snaps'])} snaps)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
