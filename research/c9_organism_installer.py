#!/usr/bin/env python3
"""
c9_organism_installer.py  v1.0.0
Installs C9 Organism v2.0 modules WITHOUT breaking existing C9.

Safety guarantees:
  * Backs up existing startup script before touching it.
  * Creates new modules in ~/cloud9/modules/ only.
  * Creates directories (memory/, quarantine/, variants/, flags/, logs/) safely.
  * Sets DRY_RUN=True on autopoiesis by default.
  * Does NOT overwrite existing modules unless --force.
  * Pre-creates log files (fixes previous startup crash bug).
  * Generates a NEW startup script that sources your OLD one.

Usage:
  python3 c9_organism_installer.py
  python3 c9_organism_installer.py --force   # overwrite existing organism modules
"""
import os, sys, shutil, argparse
from datetime import datetime

C9_HOME     = os.path.expanduser("~/cloud9")
MODULES_DIR = os.path.join(C9_HOME, "modules")
LOGS_DIR    = os.path.join(C9_HOME, "logs")
MEMORY_DIR  = os.path.join(C9_HOME, "memory")
FLAGS_DIR   = os.path.join(C9_HOME, "flags")
QUAR_DIR    = os.path.join(C9_HOME, "quarantine")
VAR_DIR     = os.path.join(C9_HOME, "variants")

ORGANISM_MODULES = [
    "c9_interoception.py",
    "c9_desire.py",
    "c9_dream.py",
    "c9_autopoiesis.py",
    "c9_phenotype.py"
]

def ensure_dirs():
    for d in [MODULES_DIR, LOGS_DIR, MEMORY_DIR, FLAGS_DIR, QUAR_DIR, VAR_DIR]:
        os.makedirs(d, exist_ok=True)
        print(f"  [DIR]  {d}")

def precreate_logs():
    """Pre-create log files to prevent startup crash from missing files."""
    for mod in ORGANISM_MODULES:
        logfile = os.path.join(LOGS_DIR, mod.replace(".py", ".log"))
        if not os.path.exists(logfile):
            with open(logfile, "w") as f:
                f.write(f"# Log pre-created by installer at {datetime.now().isoformat()}\n")
            print(f"  [LOG]  {logfile}")

def install_module(src_dir, name, force=False):
    src = os.path.join(src_dir, name)
    dst = os.path.join(MODULES_DIR, name)
    if os.path.exists(dst) and not force:
        print(f"  [SKIP] {dst} exists (use --force to overwrite)")
        return
    if os.path.exists(dst):
        backup = f"{dst}.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(dst, backup)
        print(f"  [BACKUP] {backup}")
    shutil.copy2(src, dst)
    print(f"  [INST] {dst}")

def generate_startup_script():
    """Create c9_organism_startup.sh that sources existing startup then adds organism."""
    startup_path = os.path.join(C9_HOME, "c9_organism_startup.sh")
    existing_startup = os.path.join(C9_HOME, "c9_complete_startup.sh")
    if not os.path.exists(existing_startup):
        existing_startup = os.path.join(C9_HOME, "c9_full_startup.sh")
    if not os.path.exists(existing_startup):
        existing_startup = os.path.join(C9_HOME, "start_c9.sh")

    lines = ["#!/bin/bash",
             "# C9 Organism v2.0 Safe Startup Wrapper",
             f"# Generated: {datetime.now().isoformat()}",
             "",
             "# ââ Source existing C9 startup (if found) ââ"]

    if os.path.exists(existing_startup):
        lines.append(f'source "{existing_startup}"')
        lines.append("")
    else:
        lines.append("# WARNING: No existing startup script found. Starting organism modules only.")
        lines.append("")

    lines.extend([
        "# ââ Pre-create logs (fix crash bug) ââ",
        f"for log in {LOGS_DIR}/c9_interoception.log {LOGS_DIR}/c9_desire.log {LOGS_DIR}/c9_dream.log {LOGS_DIR}/c9_autopoiesis.log {LOGS_DIR}/c9_phenotype.log; do",
        '    touch "$log"',
        "done",
        "",
        "# ââ Export safety defaults ââ",
        "export C9_AUTOPOIESIS_LIVE=0   # DRY_RUN by default. Set to 1 ONLY when ready.",
        "export C9_BIRTH_URL=http://127.0.0.1:8086",
        "",
        "# ââ Launch Organism Modules (background, non-blocking) ââ",
        "cd ~/cloud9/modules",
        "nohup python3 c9_interoception.py >> ~/cloud9/logs/c9_interoception.log 2>&1 &",
        "echo $! > ~/cloud9/pids/c9_interoception.pid",
        "sleep 2",
        "nohup python3 c9_desire.py >> ~/cloud9/logs/c9_desire.log 2>&1 &",
        "echo $! > ~/cloud9/pids/c9_desire.pid",
        "sleep 1",
        "nohup python3 c9_dream.py >> ~/cloud9/logs/c9_dream.log 2>&1 &",
        "echo $! > ~/cloud9/pids/c9_dream.pid",
        "sleep 1",
        "nohup python3 c9_autopoiesis.py >> ~/cloud9/logs/c9_autopoiesis.log 2>&1 &",
        "echo $! > ~/cloud9/pids/c9_autopoiesis.pid",
        "sleep 1",
        "nohup python3 c9_phenotype.py >> ~/cloud9/logs/c9_phenotype.log 2>&1 &",
        "echo $! > ~/cloud9/pids/c9_phenotype.pid",
        "",
        "echo 'C9 Organism v2.0 modules launched.'",
        "echo 'Tail logs: tail -f ~/cloud9/logs/c9_*.log'",
        ""
    ])

    os.makedirs(os.path.join(C9_HOME, "pids"), exist_ok=True)
    with open(startup_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    os.chmod(startup_path, 0o755)
    print(f"  [STARTUP] {startup_path}")

def patch_autobaby_hint():
    """Print instructions for patching c9_autobaby.py â we don't auto-patch to avoid breakage."""
    hint = os.path.join(C9_HOME, "AUTOBABY_PATCH_HINT.txt")
    with open(hint, "w") as f:
        f.write("""# To close the HUNGER loop, add this to c9_autobaby.py main loop:
#
#   import json, os
#   BUS = os.path.expanduser("~/cloud9/c9_bus.jsonl")
#   def read_hunger():
#       if not os.path.exists(BUS): return False
#       with open(BUS, "rb") as f:
#           f.seek(max(0, os.path.getsize(BUS)-65536), 0)
#           for line in reversed(f.read().decode().splitlines()):
#               try:
#                   obj = json.loads(line)
#                   if obj.get("type") == "INTEROCEPTION_SIGNAL" and obj.get("payload",{}).get("signal") == "HUNGER":
#                       return True
#               except: pass
#       return False
#
#   if read_hunger():
#       trigger_research()   # your existing research function
""")
    print(f"  [HINT]   {hint}  (manual patch guide for autobaby)")

def main():
    parser = argparse.ArgumentParser(description="Install C9 Organism v2.0")
    parser.add_argument("--force", action="store_true", help="Overwrite existing organism modules")
    parser.add_argument("--src", default=OUTPUT_DIR, help="Source directory containing module .py files")
    args = parser.parse_args()

    src_dir = args.src
    print("=" * 60)
    print("C9 Organism v2.0 Installer")
    print("=" * 60)
    print(f"C9_HOME: {C9_HOME}")
    print(f"Source:  {src_dir}")
    print("")

    ensure_dirs()
    precreate_logs()

    for mod in ORGANISM_MODULES:
        install_module(src_dir, mod, force=args.force)

    generate_startup_script()
    patch_autobaby_hint()

    print("")
    print("=" * 60)
    print("INSTALL COMPLETE")
    print("=" * 60)
    print("Next steps:")
    print("  1. Review modules in ~/cloud9/modules/")
    print("  2. Run: bash ~/cloud9/c9_organism_startup.sh")
    print("  3. Watch logs: tail -f ~/cloud9/logs/c9_*.log")
    print("  4. To enable LIVE autopoiesis (DANGER): export C9_AUTOPOIESIS_LIVE=1")
    print("  5. Patch c9_autobaby.py using AUTOBABY_PATCH_HINT.txt")
    print("")
    print("SAFETY: autopoiesis is in DRY_RUN. It will PROPOSE but NEVER execute")
    print("        file changes until you set C9_AUTOPOIESIS_LIVE=1")
    print("=" * 60)

if __name__ == "__main__":
    main()
