#!/usr/bin/env python3
"""
C9 Unified Launcher v2026.08.16
Runs all three integration prototypes from C9-COLLECTION-2026-0816-AUGSCIENCE.

Usage: python3 c9_unified_launcher.py [--tng] [--snn] [--birth] [--all]
"""

import argparse
import subprocess
import sys
import time
import json
from pathlib import Path

C9_BUS_PATH = Path.home() / "cloud9" / "c9_bus.jsonl"

def emit(event_type: str, data: dict):
    msg = {"t": time.time(), "event": event_type, "data": data}
    try:
        with open(C9_BUS_PATH, "a") as f:
            f.write(json.dumps(msg) + "\n")
    except Exception as e:
        print(f"[LAUNCHER] Bus error: {e}")

def run_module(name: str, script: str):
    print(f"\n{'='*60}")
    print(f"[C9-LAUNCHER] Starting {name}...")
    print(f"{'='*60}")
    try:
        result = subprocess.run(
            [sys.executable, script],
            cwd=Path(__file__).parent,
            capture_output=False,
            text=True,
            timeout=300
        )
        emit("c9_integration_complete", {
            "module": name,
            "script": script,
            "returncode": result.returncode,
            "timestamp": time.time()
        })
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"[C9-LAUNCHER] {name} timed out!")
        return False
    except Exception as e:
        print(f"[C9-LAUNCHER] {name} failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="C9 Unified Launcher")
    parser.add_argument("--tng", action="store_true", help="Run TNG bridge")
    parser.add_argument("--snn", action="store_true", help="Run SNN spin-glass")
    parser.add_argument("--birth", action="store_true", help="Run BIRTH cognitive bridge")
    parser.add_argument("--all", action="store_true", help="Run all integrations")
    args = parser.parse_args()

    if not any([args.tng, args.snn, args.birth, args.all]):
        args.all = True

    print("="*60)
    print("C9 UNIFIED LAUNCHER v2026.08.16")
    print("Collection: C9-COLLECTION-2026-0816-AUGSCIENCE")
    print("="*60)

    emit("c9_unified_launcher_start", {
        "collection": "C9-COLLECTION-2026-0816-AUGSCIENCE",
        "modules_requested": {
            "tng": args.tng or args.all,
            "snn": args.snn or args.all,
            "birth": args.birth or args.all
        }
    })

    results = {}

    if args.tng or args.all:
        results["tng"] = run_module(
            "TNG Operator Bridge",
            "integrations/c9_tng_bridge_integration.py"
        )

    if args.snn or args.all:
        results["snn"] = run_module(
            "SNN Spin-Glass",
            "integrations/c9_snn_spin_glass_lava.py"
        )

    if args.birth or args.all:
        results["birth"] = run_module(
            "BIRTH Cognitive Bridge",
            "integrations/c9_birth_cognitive_bridge.py"
        )

    print(f"\n{'='*60}")
    print("LAUNCHER SUMMARY")
    print(f"{'='*60}")
    for mod, ok in results.items():
        status = "PASS" if ok else "FAIL"
        print(f"  {mod.upper():<10} {status}")

    all_ok = all(results.values())
    emit("c9_unified_launcher_complete", {
        "results": results,
        "all_pass": all_ok,
        "timestamp": time.time()
    })

    print(f"\n[C9-LAUNCHER] All modules: {'PASS' if all_ok else 'FAIL'}")
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
