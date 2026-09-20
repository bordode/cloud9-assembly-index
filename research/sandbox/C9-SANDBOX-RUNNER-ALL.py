#!/usr/bin/env python3
"""
C9 SANDBOX MASTER RUNNER v1.0
Collection: C9-COLLECTION-2026-0825-AUGUSTSCIENCE

Executes all 5 sandbox test protocols sequentially and aggregates results
to c9_bus.jsonl compatible format.

USAGE:
  python3 C9-SANDBOX-RUNNER-ALL.py
  python3 C9-SANDBOX-RUNNER-ALL.py --test 001  # run single test
  python3 C9-SANDBOX-RUNNER-ALL.py --dna-file ~/genome/my_snps.txt
"""

import subprocess
import json
import os
import sys
import argparse
from datetime import datetime

TESTS = {
    "001": {
        "script": "C9-SANDBOX-001-GLUEBALL.py",
        "entry_id": "C9-2026-QCD-001",
        "name": "Glueball X(2370) Discovery",
        "duration_estimate": "5s"
    },
    "002": {
        "script": "C9-SANDBOX-002-KONDO.py",
        "entry_id": "C9-2026-MATSCI-002",
        "name": "Quantitative Kondo Effect",
        "duration_estimate": "10s"
    },
    "003": {
        "script": "C9-SANDBOX-003-ENTANGLEMENT.py",
        "entry_id": "C9-2026-QINFO-009",
        "name": "420 km Quantum Entanglement",
        "duration_estimate": "8s"
    },
    "004": {
        "script": "C9-SANDBOX-004-QUADRUPLE.py",
        "entry_id": "C9-2026-ASTRO-030",
        "name": "TIC 433545934 Quadruple Star",
        "duration_estimate": "15s"
    },
    "005": {
        "script": "C9-SANDBOX-005-DNA.py",
        "entry_id": "C9-2026-BIO-027",
        "name": "DNA Initiator × SNP Cross-Reference",
        "duration_estimate": "12s"
    }
}

def run_test(test_id, dna_file=None):
    """Execute a single sandbox test."""
    test = TESTS[test_id]
    script = test["script"]

    if not os.path.exists(script):
        print(f"ERROR: {script} not found. Skipping.")
        return None

    print(f"\n{'='*60}")
    print(f"RUNNING TEST {test_id}: {test['name']}")
    print(f"{'='*60}")

    cmd = [sys.executable, script]
    if test_id == "005" and dna_file:
        cmd.extend(["--snp-file", dna_file])

    try:
        result = subprocess.run(cmd, capture_output=False, text=True, timeout=120)

        # Load result JSON
        result_file = f"{test['entry_id']}_sandbox_result.json"
        if os.path.exists(result_file):
            with open(result_file, 'r') as f:
                data = json.load(f)
            return data
        else:
            print(f"WARNING: Result file {result_file} not found")
            return None

    except subprocess.TimeoutExpired:
        print(f"TIMEOUT: Test {test_id} exceeded 120s")
        return {"entry_id": test["entry_id"], "overall": "TIMEOUT"}
    except Exception as e:
        print(f"ERROR running test {test_id}: {e}")
        return {"entry_id": test["entry_id"], "overall": "ERROR"}

def main():
    parser = argparse.ArgumentParser(description="C9 Sandbox Master Runner")
    parser.add_argument("--test", nargs="+", choices=list(TESTS.keys()),
                        help="Run specific test(s) only")
    parser.add_argument("--dna-file", default=None,
                        help="Path to personal SNP file for test 005")
    parser.add_argument("--bus-output", default="c9_sandbox_results.jsonl",
                        help="Output file for bus-compatible results")
    args = parser.parse_args()

    print(f"\n{'#'*60}")
    print(f"# C9 SANDBOX MASTER RUNNER v1.0")
    print(f"# Collection: C9-COLLECTION-2026-0825-AUGUSTSCIENCE")
    print(f"# {datetime.utcnow().isoformat()}Z")
    print(f"{'#'*60}")

    test_ids = args.test if args.test else list(TESTS.keys())

    all_results = []
    pass_count = 0
    fail_count = 0

    for test_id in test_ids:
        result = run_test(test_id, args.dna_file)
        if result:
            all_results.append(result)
            if result.get("overall") == "PASS":
                pass_count += 1
            elif result.get("overall") == "FAIL":
                fail_count += 1

    # Aggregate summary
    summary = {
        "collection_id": "C9-COLLECTION-2026-0825-AUGUSTSCIENCE",
        "run_timestamp": datetime.utcnow().isoformat() + "Z",
        "n_tests": len(test_ids),
        "n_pass": pass_count,
        "n_fail": fail_count,
        "pass_rate": pass_count / len(test_ids) if test_ids else 0,
        "results": all_results
    }

    # Save aggregate
    with open("C9_SANDBOX_AGGREGATE.json", 'w') as f:
        json.dump(summary, f, indent=2)

    # Append to bus-compatible JSONL
    bus_entry = {
        "type": "sandbox_results",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "collection": "C9-COLLECTION-2026-0825-AUGUSTSCIENCE",
        "summary": {
            "n_tests": len(test_ids),
            "n_pass": pass_count,
            "n_fail": fail_count,
            "pass_rate": float(summary["pass_rate"])
        },
        "individual_results": [{"entry_id": r["entry_id"], 
                                  "overall": r.get("overall", "UNKNOWN")} 
                                 for r in all_results]
    }

    with open(args.bus_output, 'a') as f:
        f.write(json.dumps(bus_entry) + "\n")

    print(f"\n{'#'*60}")
    print(f"# AGGREGATE SUMMARY")
    print(f"{'#'*60}")
    print(f"  Tests run:   {len(test_ids)}")
    print(f"  PASS:        {pass_count}")
    print(f"  FAIL:        {fail_count}")
    print(f"  Pass rate:   {summary['pass_rate']*100:.1f}%")
    print(f"\n  Aggregate:   C9_SANDBOX_AGGREGATE.json")
    print(f"  Bus output:  {args.bus_output}")
    print(f"{'#'*60}")

if __name__ == "__main__":
    main()
