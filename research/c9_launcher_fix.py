#!/usr/bin/env python3
"""
c9_launcher_fix.py
Safely inserts well_probe into c9_unified_launcher.py MODULES list.
Creates backup first. Does NOT use string replacement on the file.
"""
import os
import json

LAUNCHER = os.path.expanduser("~/c9_unified_launcher.py")
BACKUP = LAUNCHER + ".backup." + str(int(os.path.getmtime(LAUNCHER)))

NEW_MODULE = {
    "name": "well_probe",
    "script": "c9_well_probe.py",
    "args": [],
    "port": None,
    "type": "background"
}

def main():
    if not os.path.exists(LAUNCHER):
        print("FATAL: launcher not found at", LAUNCHER)
        return

    # Create backup
    if not os.path.exists(BACKUP):
        import shutil
        shutil.copy2(LAUNCHER, BACKUP)
        print("Backup created:", BACKUP)

    with open(LAUNCHER, "r") as f:
        lines = f.readlines()

    # Find MODULES list and insert
    inserted = False
    new_lines = []
    for i, line in enumerate(lines):
        new_lines.append(line)
        if not inserted and 'MODULES' in line and ('=' in line or '[' in line):
            # Look ahead for the opening bracket or list start
            pass
        if not inserted and line.strip().startswith('MODULES') and '=' in line:
            # Next line should be [ or contain first module
            pass
        # Simple heuristic: find a line that looks like a module dict and insert after
        if not inserted and '"name":' in line and '"script":' in line:
            # We're inside the MODULES list. Insert after this module.
            indent = len(line) - len(line.lstrip())
            new_lines.append(" " * indent + json.dumps(NEW_MODULE) + ",\n")
            inserted = True
            print("Inserted well_probe after existing module")

    if not inserted:
        print("WARNING: Could not find insertion point. Manual edit required.")
        print("Add this to your MODULES list:")
        print(json.dumps(NEW_MODULE, indent=2))
        return

    with open(LAUNCHER, "w") as f:
        f.writelines(new_lines)

    print("Launcher updated successfully.")
    print("Verify with: head -20", LAUNCHER)

if __name__ == "__main__":
    main()
