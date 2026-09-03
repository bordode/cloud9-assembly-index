#!/usr/bin/env python3
"""
C9 Sandbox Test Suite — C9-2026-SPATIAL-006
Bilawal Sidhu Spatial Intelligence Stack

Tests: Verifiability, Cluster Mapping, Score Computation, Layer Assignment,
       Meta-Pattern Detection, Integration Compatibility, Bus Protocol,
       Governance Flag Validation

Usage:
    python3 c9_sandbox_spatial_006.py

Exit codes:
    0 = ALL TESTS PASSED (L1 assignment confirmed)
    1 = ONE OR MORE TESTS FAILED
"""

import json
import sys
import re
from datetime import datetime, timezone

# ── Test Configuration ──────────────────────────────────────────────────────
ENTRY_ID = "C9-2026-SPATIAL-006"
EXPECTED_LAYER = 1
EXPECTED_SCORE_MIN = 0.75
EXPECTED_SCORE_MAX = 0.90
EXPECTED_CLUSTERS = {4, 5, 6, 8}
MIN_TESTS = 8

# ── Load Entry ──────────────────────────────────────────────────────────────
try:
    with open("c9_entry_spatial_006.json", "r") as f:
        entry = json.load(f)
except FileNotFoundError:
    print(f"[FAIL] Entry file not found. Expected c9_entry_spatial_006.json")
    sys.exit(1)

results = []

def test(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append({"test": name, "status": status, "detail": detail})
    print(f"  [{status}] {name}")
    if detail:
        print(f"         → {detail}")
    return condition

print(f"\n{'='*60}")
print(f"C9 SANDBOX — {ENTRY_ID}")
print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
print(f"{'='*60}\n")

# ── TEST 1: Identity Integrity ──────────────────────────────────────────────
print("[TEST 1] Identity Integrity")
test("entry_id matches", entry.get("entry_id") == ENTRY_ID,
     f"Expected {ENTRY_ID}, got {entry.get('entry_id')}")
test("status is ACTIVE", entry.get("status") == "ACTIVE")
test("timestamp is ISO8601", bool(re.match(r"\d{4}-\d{2}-\d{2}T", entry.get("timestamp_utc", ""))))

# ── TEST 2: Verifiability ───────────────────────────────────────────────────
print("\n[TEST 2] Verifiability")
assets = entry.get("assets", [])
test("at least 2 assets", len(assets) >= 2, f"Found {len(assets)} assets")
test("all assets have public URLs", all("github.com" in a.get("url", "") for a in assets))
test("all assets MIT licensed", all(a.get("license") == "MIT" for a in assets))
test("gods-eye-view stars > 1000", any(a.get("stars", 0) > 1000 for a in assets))

# ── TEST 3: Cluster Mapping ─────────────────────────────────────────────────
print("\n[TEST 3] Cluster Mapping")
clusters = entry.get("cluster_analysis", {})
found_clusters = set()
for key in clusters:
    if key.startswith("cluster_"):
        num = int(key.split("_")[1])
        found_clusters.add(num)
test("clusters cover expected set", EXPECTED_CLUSTERS.issubset(found_clusters),
     f"Expected superset of {EXPECTED_CLUSTERS}, found {found_clusters}")
test("all cluster scores >= 0.5", all(v.get("relevance", 0) >= 0.5 for v in clusters.values()))

# ── TEST 4: Score Computation ───────────────────────────────────────────────
print("\n[TEST 4] Score Computation")
score = entry.get("audit_score", 0)
test("score in valid range", EXPECTED_SCORE_MIN <= score <= EXPECTED_SCORE_MAX,
     f"Score = {score}")

# Compute weighted composite from justification
sj = entry.get("score_justification", {})
weights = {"verifiability": 0.30, "cross_cluster_fertility": 0.30,
           "speculative_load": 0.20, "continuity_relevance": 0.20}
computed = sum(sj.get(k, {}).get("score", 0) * w for k, w in weights.items())
test("computed score matches declared", abs(computed - score) < 0.05,
     f"Declared={score}, Computed={computed:.3f}")

# ── TEST 5: Layer Assignment ────────────────────────────────────────────────
print("\n[TEST 5] Layer Assignment")
test("layer is 1 (verified)", entry.get("layer") == EXPECTED_LAYER,
     f"Layer = {entry.get('layer')}")
test("confidence is HIGH", entry.get("confidence") == "HIGH")

# ── TEST 6: Meta-Pattern Detection ──────────────────────────────────────────
print("\n[TEST 6] Meta-Pattern Detection")
meta = entry.get("meta_pattern", {})
test("meta-pattern named", bool(meta.get("name")))
test("recurrence list >= 3 entries", len(meta.get("recurrence", [])) >= 3)
test("includes self-reference", any(ENTRY_ID in r for r in meta.get("recurrence", [])))

# ── TEST 7: Bus Protocol Compatibility ──────────────────────────────────────
print("\n[TEST 7] Bus Protocol Compatibility")
test("entry_id is valid C9 format", bool(re.match(r"C9-\d{4}-[A-Z]+-\d{3}", ENTRY_ID)))
test("has related_entries array", isinstance(entry.get("related_entries"), list))
test("has tags array", isinstance(entry.get("tags"), list) and len(entry.get("tags", [])) >= 3)

# ── TEST 8: Governance Flag Validation ──────────────────────────────────────
print("\n[TEST 8] Governance Flag Validation")
integ = entry.get("integration_notes", {})
test("governance flag documented", "governance" in str(integ).lower())
test("cross-references sandbox IAI", "C9-2026-SANDBOX-IAI-001" in str(entry))

# ── Summary ─────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
passed = sum(1 for r in results if r["status"] == "PASS")
failed = sum(1 for r in results if r["status"] == "FAIL")
total = len(results)
print(f"RESULTS: {passed}/{total} passed, {failed}/{total} failed")
print(f"{'='*60}")

if failed == 0:
    print(f"\n✅ SANDBOX PASSED — {ENTRY_ID} confirmed for L1 integration.")
    # Write sandbox artifact
    artifact = {
        "entry_id": ENTRY_ID,
        "sandbox_timestamp": datetime.now(timezone.utc).isoformat(),
        "tests_total": total,
        "tests_passed": passed,
        "tests_failed": failed,
        "layer_confirmed": EXPECTED_LAYER,
        "status": "PASSED"
    }
    with open("c9_sandbox_spatial_006_result.json", "w") as f:
        json.dump(artifact, f, indent=2)
    print("   Artifact written: c9_sandbox_spatial_006_result.json")
    sys.exit(0)
else:
    print(f"\n❌ SANDBOX FAILED — {failed} test(s) failed. Entry NOT cleared for integration.")
    sys.exit(1)
